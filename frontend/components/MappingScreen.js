'use client';

import React, { useState } from 'react';
import QuestionCard from './QuestionCard';
import AnswerSheetViewer from './AnswerSheetViewer';
import {
  Award,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export default function MappingScreen({
  assessmentData,
  onOpenSummary,
}) {
  const [questions, setQuestions] = useState(assessmentData.questions || []);
  const [selectedQuestionId, setSelectedQuestionId] = useState('q2');
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState('questions'); // For mobile toggle: 'questions' | 'sheet'
  const [expandAll, setExpandAll] = useState(false);
  const [filterMode, setFilterMode] = useState('all'); // 'all' | 'answered' | 'unanswered' | 'full' | 'partial'

  const selectedQuestion = questions.find((q) => q.id === selectedQuestionId) || questions[0];

  const handleUpdateScore = (qId, newScore) => {
    setQuestions((prev) =>
      prev.map((q) =>
        q.id === qId
          ? {
              ...q,
              scoredMarks: newScore,
              status:
                newScore === q.maxMarks
                  ? 'correct'
                  : newScore === 0
                  ? 'unanswered'
                  : 'partial',
            }
          : q
      )
    );
  };

  const handleSelectQuestion = (question) => {
    setSelectedQuestionId(question.id);
    if (question.pageNumber) {
      setCurrentPage(question.pageNumber);
    }
  };

  const handleJumpToSheet = (question) => {
    setSelectedQuestionId(question.id);
    if (question.pageNumber) {
      setCurrentPage(question.pageNumber);
    }
    // On mobile, automatically switch tab to sheet
    setActiveTab('sheet');
  };

  // Filtered questions
  const filteredQuestions = questions.filter((q) => {
    if (filterMode === 'answered') return q.status !== 'unanswered' && q.scoredMarks > 0;
    if (filterMode === 'unanswered') return q.status === 'unanswered' || q.scoredMarks === 0;
    if (filterMode === 'full') return q.scoredMarks === q.maxMarks;
    if (filterMode === 'partial') return q.scoredMarks > 0 && q.scoredMarks < q.maxMarks;
    return true;
  });

  const totalMaxMarks = questions.reduce((acc, q) => acc + (q.maxMarks || 0), 0);
  const totalScoredMarks = questions.reduce((acc, q) => acc + (q.scoredMarks || 0), 0);
  const totalPercentage = totalMaxMarks > 0 ? ((totalScoredMarks / totalMaxMarks) * 100).toFixed(1) : 0;

  return (
    <div className="w-full flex-1 flex flex-col p-2 sm:p-4 md:p-6 max-w-7xl mx-auto gap-4">
      {/* Mobile Segmented Toggle Control matching Figma Phone Frames 3:1192 & 3:1576 */}
      <div className="md:hidden w-full p-1 bg-white rounded-full flex items-center shadow-md justify-between">
        <button
          onClick={() => setActiveTab('questions')}
          className={`
            flex-1 py-2.5 rounded-full font-medium text-sm transition-all text-center
            ${activeTab === 'questions'
              ? 'bg-[#303030] text-white shadow-xs'
              : 'text-[#303030] hover:bg-[#F6F6F6]'
            }
          `}
        >
          Questions
        </button>

        <button
          onClick={() => setActiveTab('sheet')}
          className={`
            flex-1 py-2.5 rounded-full font-medium text-sm transition-all text-center
            ${activeTab === 'sheet'
              ? 'bg-[#303030] text-white shadow-xs'
              : 'text-[#303030] hover:bg-[#F6F6F6]'
            }
          `}
        >
          Answer Sheet
        </button>
      </div>

      {/* Desktop Top Summary Bar */}
      <div className="hidden md:flex w-full bg-white rounded-2xl p-4 shadow-sm flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#FFF6E5] text-[#FF5623] flex items-center justify-center font-black text-sm border border-[#FFD8A8]">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-[#5D5D5D]">Total Score: </span>
              <strong className="text-sm text-[#2F2F2F] font-extrabold">
                {totalScoredMarks} / {totalMaxMarks} Marks ({totalPercentage}%)
              </strong>
            </div>
          </div>

          <div className="flex items-center gap-1 text-xs bg-[#F6F6F6] p-1 rounded-xl">
            <button
              onClick={() => setFilterMode('all')}
              className={`px-2.5 py-1 rounded-lg font-bold transition-colors ${filterMode === 'all' ? 'bg-white text-[#2F2F2F] shadow-xs' : 'text-[#5D5D5D]'}`}
            >
              All ({questions.length})
            </button>
            <button
              onClick={() => setFilterMode('answered')}
              className={`px-2.5 py-1 rounded-lg font-bold transition-colors ${filterMode === 'answered' ? 'bg-[#EAF8E6] text-[#33AC15] shadow-xs' : 'text-[#5D5D5D]'}`}
            >
              Answered (12)
            </button>
            <button
              onClick={() => setFilterMode('unanswered')}
              className={`px-2.5 py-1 rounded-lg font-bold transition-colors ${filterMode === 'unanswered' ? 'bg-[#FFE8E2] text-[#C03409] shadow-xs' : 'text-[#5D5D5D]'}`}
            >
              Unanswered (1)
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenSummary}
            className="px-3.5 py-1.5 text-xs font-bold bg-[#2F2F2F] hover:bg-black text-white rounded-xl transition-colors shadow-xs"
          >
            View Grading Report
          </button>
        </div>
      </div>

      {/* Main Grid: Desktop Side-by-Side (50% / 50%) / Mobile Tab-based */}
      <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 items-start">
        {/* Left Column: Extracted Questions (shown on desktop or when questions tab is active on mobile) */}
        <div
          className={`
            w-full flex flex-col gap-3
            ${activeTab === 'questions' ? 'flex' : 'hidden md:flex'}
          `}
        >
          {/* Header Row matching Figma Frame 1984078209 */}
          <div className="bg-white p-4 rounded-2xl shadow-sm flex items-center justify-between">
            <h2 className="text-base md:text-lg font-bold text-[#2F2F2F] tracking-tight">
              Extracted Questions (from question paper)
            </h2>
            <button
              onClick={() => setExpandAll(!expandAll)}
              className="px-3.5 py-1.5 bg-[#FFFFFF] hover:bg-[#F6F6F6] text-[#171717] text-xs font-bold rounded-xl border border-[#D0D0D0] transition-colors shadow-2xs flex items-center gap-1"
            >
              {expandAll ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              <span>{expandAll ? 'Collapse All' : 'Expand All'}</span>
            </button>
          </div>

          {/* List of Question Cards */}
          <div className="flex flex-col gap-3">
            {filteredQuestions.map((q) => (
              <QuestionCard
                key={q.id}
                question={q}
                isSelected={selectedQuestionId === q.id || expandAll}
                onSelect={handleSelectQuestion}
                onUpdateScore={handleUpdateScore}
                onJumpToSheet={handleJumpToSheet}
              />
            ))}
          </div>
        </div>

        {/* Right Column: Answer Sheet Viewer (shown on desktop or when sheet tab is active on mobile) */}
        <div
          className={`
            w-full h-[600px] md:h-[calc(100vh-140px)] sticky top-4
            ${activeTab === 'sheet' ? 'block' : 'hidden md:block'}
          `}
        >
          <AnswerSheetViewer
            pages={assessmentData.pages}
            questions={questions}
            selectedQuestion={selectedQuestion}
            onSelectQuestion={handleSelectQuestion}
            currentPage={currentPage}
            onPageChange={setCurrentPage}
            unmatchedAnswers={assessmentData.unmatchedAnswers}
          />
        </div>
      </div>
    </div>
  );
}
