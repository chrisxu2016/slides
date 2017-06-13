## ComputeEngine
这里 ComputeEngine 表示底层的计算引擎，负责各种并行任务的调度； Executor 会将所有的计算任务抽象成统一的function，异步Push到ComputeEngine中进行并行计算
，ComputeEngine 会综合参数依赖关系、计算资源的容量来优化执行顺序。

宏观思想：

- 异步Push任务，任务执行完毕返回
- 对参数的依赖，局部Read的多个function并行，局部Read和Write的函数间保持顺序
- Device统一成线程池，比如单显卡分配1个caller thread，CopyBetweenCpuGpu 等IO操作分配1 thread per GPU

模块接口：

```c++
namespace engine {
// variable存储了具体依赖的参数的信息，作为依赖的中间桥梁
struct Var;
// Fn 存储了具体执行的任务的function
struct Fn;

// variable's handle
typedef Var *VarHandle;
// function's handle
typedef Fn *FnHandle;

// 注册Var，实现 var.name -> VarHandle间的映射
// 所有Var 在ComputeEngine执行前必须注册完毕
// 任务在 Push 到 ComputeEngine前可用var.name lookup到对应的依赖参数的VarHandle
class VarRegistry {
public:
  VarHandle register(const char *name);
  VarHandle lookup(const char *name);
};

} // namespace engine

class ComputeEngine {
public:
  struct CompleteOnCompute;
  // 记录执行的环境设置，比如是否用GPU,device_id,priority等
  struct ExecContext;
  // 异步任务的打包结构
  using AsyncFn = std::function<void(ExecContext, CompleteOnCompute)>;

  // 声明资源
  // @num_cpus: cpu个数
  // @gpu_ids: 声明可用的GPU卡id
  // @num_gpu_io_thread_per_device: CPU <-> GPU 间IO线程池大小 per card
  // TODO GPU单卡线程池大小
  // TODO CPU 单核线程池大小
  ComputeEngine(int num_cpus, vector<int> gpu_ids,
                int num_gpu_io_thread_per_device, VarREgistry *var_registry);

  // 主要接口
  // @fn: 任务的function
  // @ctx: 执行环境
  // @profiled: 是否需要记录执行信息
  // Usage：
  //    fn = NewFunc(...)
  //    PushAsync(fn, ...)
  virtual void PushAsync(FnHandle fn, ExecContext ctx,
                         bool profiled = false) = 0;

  // 创建新的Function任务
  // @read_vars: 读取而不修改的Var
  // @write_vars: 修改的Var
  virtual FnHandle NewFunc(AsyncFn fn, const vector<VarHandle> &read_vars,
                           const vector<VarHandle> &write_vars) = 0;

  VarHandle LookupVar(const char *name) { return var_registry_->lookup(name); }

  // 全局单例，全局只有1个ComputeEngine
  static ComputeEngine *Global();

protected:
  // Read Write 同步相关函数 ... 略

private:
  VarRegistry *var_registry_;
};
```

所有的计算/长时IO都可以作为任务Push到ComputeEngine中，具体实现中可以有如下优化

- 对于计算任务，分CPU/GPU的device的种类，为每个device设置不同大小的线程池
- 对与长时IO任务，为每种目标device设置IO专用线程池（线程数设的小一些）
  - 可以把原有的类似 cudaMemcpy 这类IO操作，外层套上封装，如果操作memory 的size够大，则Push到ComputeEngine作为异步任务
- 在CPU上设立高优先线程池，便于GPU类的device任务的caller function优先执行

对应着实现

```c++
class ThreadPool;
class TaskQueue;
class LazyAllocatedArray; // 可以动态增长的 array
// 区分device 的ComputeEngine 实现
class ComputeEngineDeviced : public ComputeEngine {
public:
  // 这里包含具体实现
  virtual void PushAsync(FnHandle fn, ExecContext ctx,
                         const vector<VarHandle> &read_vars,
                         const vector<VarHandle> &write_vars,
                         bool profiled = false) override {
    // 按照不同的任务类型推送到不同的任务队列
    if (ctx.task_type == kGPU_COMMON || ctx.task_type == kCPU_COMMON) {
      PushToQueue(task, device_common_task_queues_[ctx.device_id]);
    } else if (ctx.task_type == kIO_CPU_to_GPU ||
               ctx.task_type == kIO_GPU_to_CPU) {
      PushToQueue(task, gpu_io_task_queues_[ctx.device_id]);
    }
    ...
  }

private:
  // 常规计算任务的线程池
  LazyAllocatedArray<ThreadPool> device_common_thread_pools_;
  LazyAllocatedArray<TaskQueue> device_common_task_queues_;
  // IO类线程池
  LazyAllocatedArray<ThreadPool> gpu_io_thread_pools_;
  LazyAllocatedArray<TaskQueue> gpu_io_task_queues_;
  // 高优先线程池
  ThreadPool high_priority_thread_pool_;
  TaskQueue high_priority_task_queue_;
};
```
