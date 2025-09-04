import { useState } from "react";
import {
  Plus,
  Calendar,
  Clock,
  Play,
  Pause,
  Trash2,
  Edit,
  Filter,
  RefreshCw,
  Settings,
} from "lucide-react";
import {
  useSchedules,
  useCreateSchedule,
  useUpdateSchedule,
  useDeleteSchedule,
  useRunNow,
} from "../hooks/useScheduler";
import { useConfig } from "../hooks/useConfig";

export default function Scheduler() {
  const [activeTab, setActiveTab] = useState("schedules");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(null);
  const [filterStatus, setFilterStatus] = useState("all");

  const { data: schedules, isLoading, refetch } = useSchedules();
  const createSchedule = useCreateSchedule();
  const updateSchedule = useUpdateSchedule();
  const deleteSchedule = useDeleteSchedule();
  const runNow = useRunNow();
  const {} = useConfig();

  const tabs = [
    { id: "schedules", name: "Scheduled Jobs", icon: Calendar },
    { id: "runs", name: "Job Runs", icon: Clock },
    { id: "settings", name: "Settings", icon: Settings },
  ];

  const statusOptions = [
    { value: "all", label: "All Statuses" },
    { value: "active", label: "Active" },
    { value: "paused", label: "Paused" },
    { value: "completed", label: "Completed" },
    { value: "failed", label: "Failed" },
  ];

  const handleCreateSchedule = async (scheduleData) => {
    try {
      await createSchedule.mutateAsync(scheduleData);
      setShowCreateModal(false);
      refetch();
    } catch (error) {
      console.error("Failed to create schedule:", error);
    }
  };

  const handleUpdateSchedule = async (id, updateData) => {
    try {
      await updateSchedule.mutateAsync({ id, ...updateData });
      setEditingSchedule(null);
      refetch();
    } catch (error) {
      console.error("Failed to update schedule:", error);
    }
  };

  const handleDeleteSchedule = async (id) => {
    if (window.confirm("Are you sure you want to delete this scheduled job?")) {
      try {
        await deleteSchedule.mutateAsync(id);
        refetch();
      } catch (error) {
        console.error("Failed to delete schedule:", error);
      }
    }
  };

  const handleRunNow = async (id) => {
    try {
      await runNow.mutateAsync({ id, idempotency_key: `manual_${Date.now()}` });
      refetch();
    } catch (error) {
      console.error("Failed to run job now:", error);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return "Not scheduled";
    // Normalize to UTC for consistent display
    const date = new Date(dateString);
    return date.toLocaleString(undefined, { timeZone: "UTC" }) + " UTC";
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "paused":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "completed":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "failed":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const filteredSchedules =
    schedules?.filter(
      (schedule) => filterStatus === "all" || schedule.status === filterStatus,
    ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Scheduler
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage automated content generation jobs
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <RefreshCw
                className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
              />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>New Schedule</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      {activeTab === "schedules" && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                >
                  {statusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {filteredSchedules.length} scheduled job
              {filteredSchedules.length !== 1 ? "s" : ""}
            </div>
          </div>

          {/* Schedules List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredSchedules.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                No scheduled jobs
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Create your first scheduled job to automate content generation
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 mx-auto"
              >
                <Plus className="w-4 h-4" />
                <span>Create Schedule</span>
              </button>
            </div>
          ) : (
            <div className="grid gap-4">
              {filteredSchedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {schedule.name || "Unnamed Job"}
                        </h3>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                            schedule.status,
                          )}`}
                        >
                          {schedule.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 dark:text-gray-400">
                        <div>
                          <span className="font-medium">Tool:</span>{" "}
                          {schedule.tool}
                        </div>
                        <div>
                          <span className="font-medium">Next Run:</span>{" "}
                          {formatDateTime(schedule.next_run_at)}
                        </div>
                        <div>
                          <span className="font-medium">Recurrence:</span>{" "}
                          {schedule.recurrence || "One-time"}
                        </div>
                      </div>

                      {schedule.input_source && (
                        <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                          <span className="font-medium">Input:</span>
                          <div className="ml-1 mt-1 p-2 bg-gray-50 dark:bg-gray-800 rounded border">
                            {typeof schedule.input_source === "string" ? (
                              <span className="break-words">
                                {schedule.input_source}
                              </span>
                            ) : schedule.input_source.text ? (
                              <span className="break-words">
                                {schedule.input_source.text}
                              </span>
                            ) : (
                              <pre className="text-xs overflow-auto">
                                {JSON.stringify(schedule.input_source, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleRunNow(schedule.id)}
                        className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-lg transition-colors"
                        title="Run now"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setEditingSchedule(schedule)}
                        className="p-2 text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteSchedule(schedule.id)}
                        className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "runs" && (
        <div className="text-center py-12">
          <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Job Runs
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            View execution history and results for your scheduled jobs
          </p>
        </div>
      )}

      {activeTab === "settings" && (
        <div className="text-center py-12">
          <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Scheduler Settings
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Configure scheduler preferences and global settings
          </p>
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreateModal || editingSchedule) && (
        <CreateScheduleModal
          schedule={editingSchedule}
          onClose={() => {
            setShowCreateModal(false);
            setEditingSchedule(null);
          }}
          onSubmit={
            editingSchedule ? handleUpdateSchedule : handleCreateSchedule
          }
        />
      )}
    </div>
  );
}

// Create/Edit Schedule Modal Component
function CreateScheduleModal({ schedule, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: schedule?.name || "",
    tool: schedule?.tool || "hello",
    input_source: schedule?.input_source || { text: "" },
    options: schedule?.options || {},
    run_at: schedule?.next_run_at
      ? new Date(schedule.next_run_at).toISOString().slice(0, 16)
      : "",
    recurrence: schedule?.recurrence || "none",
    timezone: schedule?.timezone || "UTC",
    max_runs: schedule?.max_runs || null,
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const submitData = {
      ...formData,
      run_at: formData.run_at ? new Date(formData.run_at + "Z") : null, // Ensure UTC
      max_runs: formData.max_runs ? parseInt(formData.max_runs) : null,
    };

    if (schedule) {
      onSubmit(schedule.id, submitData);
    } else {
      onSubmit(submitData);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {schedule ? "Edit Schedule" : "Create New Schedule"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Job Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter a name for this scheduled job"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tool
            </label>
            <select
              value={formData.tool}
              onChange={(e) => handleInputChange("tool", e.target.value)}
              className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="hello">Hello World</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Input Text
            </label>
            <textarea
              value={formData.input_source.text || ""}
              onChange={(e) =>
                handleInputChange("input_source", { text: e.target.value })
              }
              className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={4}
              placeholder="Enter the content to be processed..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Run At
              </label>
              <input
                type="datetime-local"
                value={formData.run_at}
                onChange={(e) => handleInputChange("run_at", e.target.value)}
                className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Recurrence
              </label>
              <select
                value={formData.recurrence}
                onChange={(e) =>
                  handleInputChange("recurrence", e.target.value)
                }
                className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="none">One-time</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {schedule ? "Update Schedule" : "Create Schedule"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
