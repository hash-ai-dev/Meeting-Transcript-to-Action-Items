import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Loader2, CheckCircle, Circle, Trash2,
  Save, FolderOpen, Plus, AlertCircle, FileText,
  Brain, Sparkles
} from 'lucide-react';
import './index.css';

const API_URL = "http://localhost:5000";

export default function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({
    transcript: [],
    action_items: [],
    important_notes: []
  });
  const [sessions, setSessions] = useState([]);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [sessionName, setSessionName] = useState("");

  // Fetch data from backend
  const fetchData = async () => {
    try {
      const res = await axios.get(`${API_URL}/status?t=${Date.now()}`);
      setData(res.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // Fetch saved sessions
  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API_URL}/list_sessions`);
      setSessions(res.data.sessions || []);
    } catch (error) {
      console.error("Error fetching sessions:", error);
    }
  };

  useEffect(() => {
    fetchData();
    fetchSessions();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Process text
  const handleAnalyze = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      await axios.post(`${API_URL}/process_text`, { text: input });
      setInput("");
      await fetchData();
    } catch (error) {
      console.error("Error processing text:", error);
    }
    setLoading(false);
  };

  // Toggle task completion
  const handleToggle = async (index) => {
    try {
      await axios.post(`${API_URL}/toggle_task`, { index });
      await fetchData();
    } catch (error) {
      console.error("Error toggling task:", error);
    }
  };

  // Save session
  const handleSave = async () => {
    if (!sessionName.trim()) return;
    try {
      await axios.post(`${API_URL}/save_session`, { title: sessionName });
      setShowSaveModal(false);
      setSessionName("");
      await fetchSessions();
    } catch (error) {
      console.error("Error saving session:", error);
    }
  };

  // Load session
  const handleLoad = async (filename) => {
    try {
      await axios.post(`${API_URL}/load_session`, { filename });
      await fetchData();
      setShowLoadModal(false);
    } catch (error) {
      console.error("Error loading session:", error);
    }
  };

  // Delete session
  const handleDelete = async (filename, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this session?")) return;
    try {
      await axios.delete(`${API_URL}/delete_session`, { data: { filename } });
      await fetchSessions();
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  // Reset
  const handleReset = async () => {
    if (!window.confirm("Reset all data?")) return;
    try {
      await axios.post(`${API_URL}/reset`);
      await fetchData();
    } catch (error) {
      console.error("Error resetting:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">Meeting Intelligence</h1>
                <p className="text-xs text-slate-500">AI-Powered Action Extractor</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowLoadModal(true)}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors flex items-center gap-2"
                aria-label="Load session"
              >
                <FolderOpen className="w-4 h-4" />
                <span className="hidden sm:inline">Load</span>
              </button>
              <button
                onClick={() => setShowSaveModal(true)}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors flex items-center gap-2"
                aria-label="Save session"
              >
                <Save className="w-4 h-4" />
                <span className="hidden sm:inline">Save</span>
              </button>
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                aria-label="Reset all"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline">Reset</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Hero Section */}
        <section className="mb-8">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                  Extract Action Items from Meetings
                </h2>
                <p className="text-slate-600">
                  Paste your meeting transcript below and let AI identify action items, owners, and deadlines automatically.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleAnalyze();
                  }
                }}
                placeholder="Paste your meeting transcript here... (Ctrl+Enter to analyze)"
                className="w-full h-40 px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-slate-900 placeholder-slate-400"
                aria-label="Meeting transcript input"
              />

              <button
                onClick={handleAnalyze}
                disabled={loading || !input.trim()}
                className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/30"
                aria-label="Analyze transcript"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Analyze Transcript</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {/* Results Grid */}
        <div className="grid lg:grid-cols-2 gap-6">

          {/* Action Items */}
          <section>
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">Action Items</h3>
                    <p className="text-sm text-slate-500">
                      {data.action_items.filter(item => !item.done).length} pending
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3 max-h-[500px] overflow-y-auto scrollbar-hide">
                <AnimatePresence>
                  {data.action_items.length > 0 && (
                    data.action_items.map((item, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className={`p-4 rounded-xl border transition-all cursor-pointer ${item.done
                          ? 'bg-green-50 border-green-200'
                          : 'bg-slate-50 border-slate-200 hover:border-blue-300 hover:shadow-sm'
                          }`}
                        onClick={() => handleToggle(index)}
                        role="button"
                        tabIndex={0}
                        aria-label={`Toggle task: ${item.task}`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5">
                            {item.done ? (
                              <CheckCircle className="w-5 h-5 text-green-600" />
                            ) : (
                              <Circle className="w-5 h-5 text-slate-400" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`font-medium mb-1 ${item.done ? 'text-slate-500 line-through' : 'text-slate-900'
                              }`}>
                              {item.task}
                            </p>
                            <div className="flex flex-wrap gap-2 text-xs">
                              {item.owner && (
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-md font-medium">
                                  {item.owner}
                                </span>
                              )}
                              {item.deadline && (
                                <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded-md font-medium">
                                  {item.deadline}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </AnimatePresence>
              </div>
            </div>
          </section>

          {/* Important Notes */}
          <section>
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">Important Notes</h3>
                  <p className="text-sm text-slate-500">{data.important_notes.length} items</p>
                </div>
              </div>

              <div className="space-y-3 max-h-[500px] overflow-y-auto scrollbar-hide">
                {data.important_notes.length > 0 && (
                  data.important_notes.map((note, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 bg-amber-50 border border-amber-200 rounded-xl"
                    >
                      <p className="text-slate-700 leading-relaxed">{note}</p>
                    </motion.div>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Save Modal */}
      <AnimatePresence>
        {showSaveModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6"
              role="dialog"
              aria-labelledby="save-modal-title"
            >
              <h3 id="save-modal-title" className="text-xl font-bold text-slate-900 mb-4">
                Save Session
              </h3>
              <input
                type="text"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSave()}
                placeholder="Enter session name..."
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
                autoFocus
                aria-label="Session name"
              />
              <div className="flex gap-3">
                <button
                  onClick={() => setShowSaveModal(false)}
                  className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={!sessionName.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Save
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Load Modal */}
      <AnimatePresence>
        {showLoadModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6"
              role="dialog"
              aria-labelledby="load-modal-title"
            >
              <h3 id="load-modal-title" className="text-xl font-bold text-slate-900 mb-4">
                Load Session
              </h3>
              <div className="space-y-2 max-h-96 overflow-y-auto mb-4">
                {sessions.length === 0 ? (
                  <p className="text-center py-8 text-slate-400">No saved sessions</p>
                ) : (
                  sessions.map((session) => (
                    <div
                      key={session.filename}
                      className="p-4 border border-slate-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-all group"
                      onClick={() => handleLoad(session.filename)}
                      role="button"
                      tabIndex={0}
                      aria-label={`Load session: ${session.title}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-slate-900">{session.title}</p>
                          <p className="text-sm text-slate-500">
                            {session.item_count} items • {session.note_count} notes
                          </p>
                        </div>
                        <button
                          onClick={(e) => handleDelete(session.filename, e)}
                          className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                          aria-label="Delete session"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <button
                onClick={() => setShowLoadModal(false)}
                className="w-full px-4 py-2 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-colors"
              >
                Close
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
