'use client';

import React from 'react';
import {
  X,
  Award,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  FileDown,
  Printer,
  Sparkles,
  BookOpen,
} from 'lucide-react';

export default function GradingSummaryModal({
  isOpen,
  onClose,
  assessmentData,
  questions = [],
}) {
  if (!isOpen) return null;

  const totalMax = questions.reduce((acc, q) => acc + (q.maxMarks || 0), 0);
  const totalScored = questions.reduce((acc, q) => acc + (q.scoredMarks || 0), 0);
  const percentage = totalMax > 0 ? ((totalScored / totalMax) * 100).toFixed(1) : 0;

  const fullCount = questions.filter((q) => q.scoredMarks === q.maxMarks).length;
  const partialCount = questions.filter(
    (q) => q.scoredMarks > 0 && q.scoredMarks < q.maxMarks
  ).length;
  const zeroCount = questions.filter(
    (q) => q.scoredMarks === 0 || q.status === 'unanswered'
  ).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-[#E5E5E5] flex flex-col">
        {/* Modal Header */}
        <div className="p-6 border-b border-[#EAEAEA] flex items-center justify-between sticky top-0 bg-white z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-[#FFF6E5] text-[#FF5623] flex items-center justify-center border border-[#FFD8A8]">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#2F2F2F]">
                Assessment Grading Summary
              </h3>
              <p className="text-xs text-[#5D5D5D]">
                {assessmentData?.title || 'Class 10 Biology Unit Test'} • Student: {assessmentData?.studentName || 'Aarav Sharma'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-[#F6F6F6] hover:bg-[#EFEFEF] flex items-center justify-center text-[#5D5D5D] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 flex flex-col gap-6">
          {/* Main Score Banner */}
          <div className="bg-gradient-to-tr from-[#2A2A2A] to-[#171717] text-white rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 shadow-md">
            <div className="flex flex-col items-center md:items-start text-center md:text-left">
              <span className="text-xs text-[#A9A9A9] font-medium tracking-wide uppercase">
                Final Score Achieved
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-4xl md:text-5xl font-black text-[#5DFF35]">
                  {totalScored}
                </span>
                <span className="text-2xl font-bold text-white/60">
                  / {totalMax} Marks
                </span>
              </div>
              <span className="text-xs text-[#EAEAEA] mt-1">
                Grade: <strong className="text-[#5DFF35] font-extrabold">{percentage >= 80 ? 'A (Distinction)' : percentage >= 60 ? 'B (Proficient)' : 'C (Needs Review)'}</strong> ({percentage}%)
              </span>
            </div>

            {/* Score Metric Badges */}
            <div className="grid grid-cols-3 gap-3 w-full md:w-auto">
              <div className="bg-white/10 p-3 rounded-xl text-center border border-white/10">
                <span className="text-lg font-black text-[#5DFF35]">{fullCount}</span>
                <p className="text-[10px] text-white/80 font-medium">Full Marks</p>
              </div>
              <div className="bg-white/10 p-3 rounded-xl text-center border border-white/10">
                <span className="text-lg font-black text-[#FF934F]">{partialCount}</span>
                <p className="text-[10px] text-white/80 font-medium">Partial</p>
              </div>
              <div className="bg-white/10 p-3 rounded-xl text-center border border-white/10">
                <span className="text-lg font-black text-[#FF5623]">{zeroCount}</span>
                <p className="text-[10px] text-white/80 font-medium">Unanswered</p>
              </div>
            </div>
          </div>

          {/* AI Comprehensive Insights */}
          <div className="p-4 bg-[#F9F9F9] rounded-2xl border border-[#EAEAEA] flex flex-col gap-3">
            <div className="flex items-center gap-2 text-sm font-bold text-[#2F2F2F]">
              <Sparkles className="w-4 h-4 text-[#FF5623]" />
              <span>Overall AI Examiner Feedback</span>
            </div>
            <p className="text-xs text-[#5D5D5D] leading-relaxed">
              Student demonstrates strong foundational understanding of cellular respiration, plant vascular biology, and renal anatomy. Excellent diagrammatic representations for nephron and alveolus structures. Primary areas for growth include cardiac circulation (skipped question 4) and ecological adaptation recovery steps (question 11b).
            </p>
          </div>

          {/* Question Breakdown Table */}
          <div className="flex flex-col gap-2">
            <h4 className="text-sm font-bold text-[#2F2F2F]">
              Question-wise Marks Table
            </h4>
            <div className="border border-[#E5E5E5] rounded-xl overflow-hidden text-xs">
              <table className="w-full text-left">
                <thead className="bg-[#F6F6F6] text-[#5D5D5D] border-b border-[#E5E5E5] font-semibold">
                  <tr>
                    <th className="p-2.5">Q#</th>
                    <th className="p-2.5">Concept / Topic</th>
                    <th className="p-2.5">Max</th>
                    <th className="p-2.5">Scored</th>
                    <th className="p-2.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E5E5E5]">
                  {questions.map((q) => (
                    <tr key={q.id} className="hover:bg-[#FAFAFA]">
                      <td className="p-2.5 font-bold text-[#2F2F2F]">
                        Q{q.displayNumber}
                      </td>
                      <td className="p-2.5 text-[#5D5D5D] truncate max-w-[200px]">
                        {q.text}
                      </td>
                      <td className="p-2.5 text-[#5D5D5D]">{q.maxMarks}</td>
                      <td className="p-2.5 font-bold text-[#2F2F2F]">{q.scoredMarks}</td>
                      <td className="p-2.5">
                        <span
                          className={`
                            px-2 py-0.5 rounded-full text-[10px] font-bold
                            ${q.scoredMarks === q.maxMarks
                              ? 'bg-[#EAF8E6] text-[#33AC15]'
                              : q.scoredMarks > 0
                              ? 'bg-[#FFF6E5] text-[#E2600E]'
                              : 'bg-[#FFE8E2] text-[#C03409]'
                            }
                          `}
                        >
                          {q.scoredMarks === q.maxMarks
                            ? 'Full'
                            : q.scoredMarks > 0
                            ? 'Partial'
                            : '0 Marks'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-[#EAEAEA] bg-[#F9F9F9] flex items-center justify-between sticky bottom-0">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-4 py-2 bg-white hover:bg-[#EFEFEF] text-[#2F2F2F] text-xs font-bold rounded-xl border border-[#D0D0D0] transition-colors shadow-xs"
          >
            <Printer className="w-4 h-4" />
            <span>Print Report</span>
          </button>

          <button
            onClick={onClose}
            className="px-6 py-2 bg-[#2F2F2F] hover:bg-black text-white text-xs font-bold rounded-xl transition-colors shadow-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
