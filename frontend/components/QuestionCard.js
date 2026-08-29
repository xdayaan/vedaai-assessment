'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Eye, Sparkles, Edit3, Check, AlertTriangle } from 'lucide-react';

export default function QuestionCard({
  question,
  isSelected,
  onSelect,
  onUpdateScore,
  onJumpToSheet,
}) {
  const [isExpanded, setIsExpanded] = useState(isSelected || false);
  const [isEditingScore, setIsEditingScore] = useState(false);
  const [editMarks, setEditMarks] = useState(question.scoredMarks);

  // Sync expanded state when selected externally
  React.useEffect(() => {
    if (isSelected) {
      setIsExpanded(true);
    }
  }, [isSelected]);

  const toggleExpand = (e) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
    if (!isSelected) {
      onSelect(question);
    }
  };

  const handleCardClick = () => {
    onSelect(question);
    setIsExpanded(true);
  };

  const handleSaveScore = (e) => {
    e.stopPropagation();
    const parsed = Math.max(0, Math.min(question.maxMarks, Number(editMarks) || 0));
    onUpdateScore(question.id, parsed);
    setIsEditingScore(false);
  };

  // Status color styles
  const isFull = question.scoredMarks === question.maxMarks;
  const isZero = question.scoredMarks === 0 || question.status === 'unanswered';
  const isPartial = !isFull && !isZero;

  const scoreBadgeBg = isFull
    ? 'bg-[#EAF8E6] text-[#33AC15] border-[#D4F2CA]'
    : isPartial
    ? 'bg-[#FFF6E5] text-[#E2600E] border-[#FFD8A8]'
    : 'bg-[#FFE8E2] text-[#C03409] border-[#FFC8B8]';

  return (
    <div
      onClick={handleCardClick}
      className={`
        w-full rounded-2xl transition-all cursor-pointer
        ${isSelected
          ? 'bg-white border-2 border-[#FF8D36] shadow-md'
          : 'bg-white hover:bg-[#FAFAFA] shadow-xs'
        }
      `}
    >
      {/* Top Header Row matching Figma */}
      <div className="p-4 flex items-start gap-3 justify-between">
        {/* Left: Number & Text */}
        <div className="flex items-start gap-3 min-w-0 flex-1">
          {/* Question Number Badge */}
          {question.subPart ? (
            <div className="flex items-center gap-1 shrink-0">
              <div
                className={`
                  w-8 h-8 rounded-lg flex items-center justify-center text-sm font-extrabold transition-colors
                  ${isSelected
                    ? 'bg-[#FF5623] text-white shadow-xs'
                    : 'bg-[#2A2A2A] text-white'
                  }
                `}
              >
                {question.questionNumber}
              </div>
              <div className="w-8 h-8 rounded-lg bg-[#F6F6F6] text-[#2F2F2F] font-bold text-sm flex items-center justify-center border border-[#E5E5E5]">
                {question.subPart}.
              </div>
            </div>
          ) : (
            <div
              className={`
                w-8 h-8 rounded-lg flex items-center justify-center text-sm font-extrabold shrink-0 transition-colors
                ${isSelected
                  ? 'bg-[#FF5623] text-white shadow-xs'
                  : 'bg-[#2A2A2A] text-white'
                }
              `}
            >
              {question.questionNumber}
            </div>
          )}

          {/* Question Description */}
          <div className="flex flex-col gap-1 min-w-0 flex-1">
            <p className="text-sm md:text-base font-normal text-[#2F2F2F] leading-snug">
              {question.text}
            </p>
            {question.status === 'unanswered' && (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#C03409] bg-[#FFE8E2] px-2 py-0.5 rounded-md w-fit">
                <AlertTriangle className="w-3 h-3" /> Unanswered / Skipped
              </span>
            )}
          </div>
        </div>

        {/* Right: Score Pill & Expand button */}
        <div className="flex items-center gap-2 shrink-0 ml-2">
          {isEditingScore ? (
            <div
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-1 bg-[#F6F6F6] p-1 rounded-lg border border-[#D0D0D0]"
            >
              <input
                type="number"
                min="0"
                max={question.maxMarks}
                value={editMarks}
                onChange={(e) => setEditMarks(e.target.value)}
                className="w-10 text-center font-bold text-sm bg-white border border-[#CDCDCD] rounded px-1 py-0.5 text-[#2F2F2F]"
              />
              <span className="text-xs text-[#5D5D5D]">/ {question.maxMarks}</span>
              <button
                onClick={handleSaveScore}
                className="w-6 h-6 rounded bg-[#33AC15] text-white flex items-center justify-center hover:bg-[#2A9310]"
              >
                <Check className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div
              onClick={(e) => {
                e.stopPropagation();
                setIsEditingScore(true);
              }}
              className={`
                px-3 py-1 rounded-lg text-sm font-bold border flex items-center gap-1.5 transition-all
                ${scoreBadgeBg}
              `}
              title="Click to edit score"
            >
              <span>
                {question.scoredMarks} / {question.maxMarks}
              </span>
              <Edit3 className="w-3 h-3 opacity-60 hover:opacity-100" />
            </div>
          )}

          {/* Expand/Collapse Chevron Button */}
          <button
            onClick={toggleExpand}
            className="w-7 h-7 rounded-lg bg-[#F6F6F6] hover:bg-[#EFEFEF] flex items-center justify-center text-[#2F2F2F] transition-colors border border-[#E5E5E5]"
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Expanded Content Section matching Figma */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-1 flex flex-col gap-3 border-t border-[#F0F0F0] mt-1">
          {/* AI Suggested Sub-header */}
          <div className="flex items-center justify-between text-xs text-[#5D5D5D] pt-2">
            <span className="font-semibold text-[#5D5D5D]">
              AI Suggested : {question.aiSuggestedMarks} / {question.maxMarks}
            </span>
            {question.boundingBox && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onJumpToSheet(question);
                }}
                className="flex items-center gap-1 text-[#FF5623] hover:text-[#C03409] font-bold text-xs"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>View on Answer Sheet (Page {question.pageNumber})</span>
              </button>
            )}
          </div>

          {/* AI Feedback Card matching Figma */}
          <div className="p-3.5 bg-[#F6F6F6] rounded-xl flex flex-col gap-1.5 border border-[#EAEAEA]">
            <div className="flex items-center gap-1.5 text-xs font-bold text-[#2F2F2F]">
              <Sparkles className="w-3.5 h-3.5 text-[#FF5623]" />
              <span>AI Feedback</span>
            </div>
            <p className="text-xs md:text-sm text-[#2F2F2F] leading-relaxed">
              {question.aiFeedback}
            </p>
          </div>

          {/* Student Answer Transcribed Snippet */}
          {question.studentAnswerText && (
            <div className="text-xs text-[#5D5D5D] bg-[#FAFAFA] p-2.5 rounded-lg border border-[#EAEAEA]">
              <span className="font-semibold text-[#2F2F2F]">Transcribed Student Answer: </span>
              <span className="italic">"{question.studentAnswerText}"</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
