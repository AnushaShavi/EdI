public class Task {
    public string Description { get; private set; }
    public DateTime StartTime { get; private set; }
    public DateTime EndTime { get; private set; }
    public string Priority { get; private set; }
    public bool IsCompleted { get; set; }

    public Task(string description, DateTime startTime, DateTime endTime, string priority) {
        Description = description;
        StartTime = startTime;
        EndTime = endTime;
        Priority = priority;
        IsCompleted = false;
    }

    public override string ToString() {
        return $"{StartTime:HH:mm} - {EndTime:HH:mm}: {Description} [{Priority}]";
    }
}
public static class TaskFactory {
    public static Task CreateTask(string description, string startTime, string endTime, string priority) {
        DateTime start;
        DateTime end;

        if (!DateTime.TryParse(startTime, out start) || !DateTime.TryParse(endTime, out end) || start >= end) {
            throw new ArgumentException("Invalid time format or start time must be before end time.");
        }

        return new Task(description, start, end, priority);
    }
}
public class ScheduleManager {
    private static ScheduleManager _instance;
    private List<Task> _tasks;
    private List<IObserver> _observers;

    private ScheduleManager() {
        _tasks = new List<Task>();
        _observers = new List<IObserver>();
    }

    public static ScheduleManager GetInstance() {
        if (_instance == null) {
            _instance = new ScheduleManager();
        }
        return _instance;
    }

    public void AddObserver(IObserver observer) {
        _observers.Add(observer);
    }

    private void NotifyObservers(Task task) {
        foreach (var observer in _observers) {
            observer.OnTaskAdded(task, _tasks);
        }
    }

    public void AddTask(Task task) {
        foreach (var existingTask in _tasks) {
            if (task.StartTime < existingTask.EndTime && task.EndTime > existingTask.StartTime) {
                throw new InvalidOperationException($"Task conflicts with existing task \"{existingTask.Description}\".");
            }
        }
        _tasks.Add(task);
        NotifyObservers(task);
    }

    public void RemoveTask(string description) {
        var task = _tasks.Find(t => t.Description == description);
        if (task != null) {
            _tasks.Remove(task);
        } else {
            throw new ArgumentException("Task not found.");
        }
    }

    public void ViewTasks() {
        if (_tasks.Count == 0) {
            Console.WriteLine("No tasks scheduled for the day.");
        } else {
            foreach (var task in _tasks.OrderBy(t => t.StartTime)) {
                Console.WriteLine(task);
            }
        }
    }
}
public interface IObserver {
    void OnTaskAdded(Task newTask, List<Task> allTasks);
}

public class TaskConflictNotifier : IObserver {
    public void OnTaskAdded(Task newTask, List<Task> allTasks) {
        foreach (var task in allTasks) {
            if (newTask != task && newTask.StartTime < task.EndTime && newTask.EndTime > task.StartTime) {
                Console.WriteLine($"Conflict Alert: New task \"{newTask.Description}\" conflicts with \"{task.Description}\".");
            }
        }
    }
}
public class Program {
    public static void Main(string[] args) {
        ScheduleManager manager = ScheduleManager.GetInstance();
        TaskConflictNotifier conflictNotifier = new TaskConflictNotifier();
        manager.AddObserver(conflictNotifier);

        try {
            var task1 = TaskFactory.CreateTask("Morning Exercise", "07:00", "08:00", "High");
            manager.AddTask(task1);
            
            var task2 = TaskFactory.CreateTask("Team Meeting", "09:00", "10:00", "Medium");
            manager.AddTask(task2);

            manager.ViewTasks();
        } catch (Exception ex) {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
