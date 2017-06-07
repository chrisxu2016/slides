class: center, middle, inverse

<style>
.highlight {
color: red;
text-weight: bold;
}
</style>

# mxnet::engine 调研
<p align="center">yanchunwei@baidu</p>
---
# 模块功能简介

- 按照依赖关系执行多个 function
  - 有依赖关系的 function 必须依次执行
  - 无依赖关系的 function 间并行执行
- 可以用于宏观任务
  - 比如 Makefile 中的依赖

---

# API && 功能简介
```c++
virtual void PushSync(Fn exec_fun, Context exec_ctx,
                          std::vector<VarHandle> const& const_vars,
                          std::vector<VarHandle> const& mutate_vars) = 0;
```

- `exec_fun`： 待执行的 function
- `exec_ctx`： 执行的上下文信息
- `const_vars`：不可变参数
- `mutate_vars`：可变参数

---
## exec_fun

- 单线程 engine 的function
```c++
using Fn = std::function<void(RunContext)>;
```

- 多线程异步engine 的function
```c++
// Callback will be called once the function is exectuated.
using Callback = std::function<void()>;
using AsyncFn = std::function<void(RunContext, Callback)>;
```

---
## exec_ctx
对应 context一般存储执行时的一些信息，比如：

- function 在 CPU/GPU 执行
- GPU，对应的 streaming

```c++
struct RunContext {
    // stream pointer which could be safely cast to
    // cudaStream_t* type
    void *stream;
};
```

---
## var 构建function依赖关系
### VarHandle
- 表示资源的tag
- 用来构建依赖关系
- `const_vars` 和 `mutate_vars` 表示不同的依赖关系

---
## var 构建function依赖关系
### 基于Var的function间调度的原则

- The execution of any two functions when <span class="highlight">one of them</span> modifies 
at least <span class="highlight">one common variable</span> is serialized in their push order.

比如：

```
Push Fn1(mutate V2)
Push Fn2(mutate V2)

or 

Push Fn1(mutate V2)
Push Fn2(const V2)
// or reverse

will execute in order:  Fn1 -> Fn2

Push Fn1(const V2)
Push Fn2(const V2)

will execute in random order (or run in parallel)
```
---
## var 构建function依赖关系
### 基于Var的function间调度的原则
此规则可以节约内存分配，比如

```
A += B

will execute in order:

A <- A + B

not:

tmp <- A + B (malloc tmp)
A <- tmp (delloc tmp/A)
```

## Push and Wait
- 所有的 `Push` 均异步
- 如果需要等 `Fn` 跑完执行后面的操作，可以在Push时附带一个 Callback(OnComplete)
- `WaitForVar(var)` 等待直到指定 `var` 的所有读写操作的 Fn 均执行完毕
- `WaitForAll()` 等待所有Push到engine的 Fn 执行完毕

## Save Object Creation Cost
- 高频Push同一个Fn，需要减少lambda function 的消耗

```c++
virtual OprHandle NewOperator(AsyncFn fn,
                                  std::vector<VarHandle> const& const_vars,
                                  std::vector<VarHandle> const& mutate_vars) = 0;

virtual void Push(OprHandle op, Context exec_ctx) = 0;
```
# 代码实现
## 代码结构

| mxnet/include/engine.h | engine对外接口 |
| mxnet/engine/engine.cc |                |
|                        |                |

---
# 参考文献
1. [mxnet overview](http://mxnet.io/architecture/overview.html)
