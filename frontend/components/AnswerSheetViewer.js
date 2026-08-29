'use client';

import React, { useRef, useState, useEffect } from 'react';
import {
  Minus,
  Plus,
  Maximize2,
  Minimize2,
  RotateCcw,
  Sparkles,
  Info,
  Layers,
  FileText,
} from 'lucide-react';

export default function AnswerSheetViewer({
  pages = [],
  questions = [],
  selectedQuestion,
  onSelectQuestion,
  unmatchedAnswers = [],
}) {
  const [zoom, setZoom] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);
  const highlightRefs = useRef({});

  // When selectedQuestion changes, smoothly scroll the highlighted element into view
  useEffect(() => {
    if (selectedQuestion && selectedQuestion.id) {
      setTimeout(() => {
        const el = highlightRefs.current[selectedQuestion.id];
        if (el && containerRef.current) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 150);
    }
  }, [selectedQuestion]);

  const handleZoomIn = () => setZoom((z) => Math.min(200, z + 20));
  const handleZoomOut = () => setZoom((z) => Math.max(60, z - 20));
  const handleResetZoom = () => setZoom(100);

  // If pages array is empty, provide a fallback 1-page item
  const displayPages = pages.length > 0 ? pages : [
    { pageNumber: 1, image: '/images/answer_sheet_page_1.png', label: 'Page 1' }
  ];

  const totalMapped = questions.filter((q) => q.boundingBox || (q.bboxes && q.bboxes.length > 0)).length;

  return (
    <div
      className={`
        w-full h-full flex flex-col bg-white rounded-2xl overflow-hidden shadow-md
        ${isFullscreen ? 'fixed inset-0 z-50 rounded-none' : 'relative'}
      `}
    >
      {/* Top Header Controls Bar matching Figma (Dark #2F2F2F) */}
      <div className="bg-[#2F2F2F] text-white px-4 md:px-6 py-3 flex items-center justify-between z-20 shrink-0 select-none">
        {/* Left: Title */}
        <div className="flex items-center gap-2">
          <span className="text-base font-bold text-white tracking-tight">
            Answer Sheet
          </span>
          <span className="text-xs text-[#A9A9A9] hidden sm:inline">
            (Handwritten Student Script)
          </span>
        </div>

        {/* Right: Zoom Controls & Scroll Indicator */}
        <div className="flex items-center gap-2 md:gap-4">
          {/* Zoom Control Group */}
          <div className="flex items-center gap-1 bg-[#171717] px-2.5 py-1 rounded-xl border border-white/10 text-xs font-semibold">
            <button
              type="button"
              onClick={handleZoomOut}
              className="p-1 hover:text-[#FF5623] text-white transition-colors cursor-pointer"
              title="Zoom Out"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
            <span
              onClick={handleResetZoom}
              className="px-1.5 cursor-pointer hover:text-[#FF934F] min-w-[40px] text-center"
              title="Reset Zoom (100%)"
            >
              {zoom}%
            </span>
            <button
              type="button"
              onClick={handleZoomIn}
              className="p-1 hover:text-[#FF5623] text-white transition-colors cursor-pointer"
              title="Zoom In"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Continuous Pages Badge */}
          <div className="hidden sm:flex items-center gap-1.5 bg-[#171717] px-3 py-1 rounded-xl border border-white/10 text-xs font-semibold text-[#E0E0E0]">
            <FileText className="w-3.5 h-3.5 text-[#FF5623]" />
            <span>{displayPages.length} {displayPages.length === 1 ? 'Page' : 'Pages'} (Scrollable)</span>
          </div>

          {/* Fullscreen Toggle */}
          <button
            type="button"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-xl bg-[#171717] hover:bg-[#3F3F3F] text-white transition-colors border border-white/10 cursor-pointer"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Answer Sheet Continuous Vertical Scroll Feed */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto overflow-x-hidden bg-[#ECECEC] relative p-4 md:p-6 flex flex-col items-center gap-6 select-none scroll-smooth"
      >
        {displayPages.map((pageData) => {
          const pNum = pageData.pageNumber;

          // Find questions that belong to or span this page
          const questionsOnThisPage = questions.filter((q) => {
            if (q.pageNumber === pNum && q.boundingBox) return true;
            if (q.spansPages && q.spansPages.includes(pNum)) return true;
            if (q.bboxes && q.bboxes.some((b) => b.page === pNum)) return true;
            return false;
          });

          // Unmatched scribbles on this page
          const unmatchedOnThisPage = unmatchedAnswers.filter(
            (u) => u.pageNumber === pNum
          );

          return (
            <div
              key={pNum}
              className="flex flex-col items-center w-full transition-all duration-200"
            >
              {/* Page Number Divider Tag */}
              <div className="mb-2 px-3 py-0.5 rounded-full bg-white/90 shadow-2xs border border-[#D5D5D5] text-[11px] font-bold text-[#5D5D5D] flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#FF5623]" />
                <span>Page {pNum} of {displayPages.length}</span>
              </div>

              {/* Page Image & Bounding Box Overlay Canvas */}
              <div
                className="relative bg-white shadow-2xl rounded-xl overflow-hidden origin-top transition-all duration-200 border border-[#E0E0E0]"
                style={{
                  width: `${(658 * zoom) / 100}px`,
                  maxWidth: '100%',
                }}
              >
                {/* Main Page Image */}
                <img
                  src={pageData.image || '/images/answer_sheet_page_1.png'}
                  alt={`Answer sheet page ${pNum}`}
                  className="w-full h-auto block select-none pointer-events-none"
                  loading="lazy"
                />

                {/* Render Bounding Box Overlays for all questions on this page */}
                {questionsOnThisPage.map((q) => {
                  const isSelected = selectedQuestion?.id === q.id;

                  // Determine bounding box for this specific page
                  let bbox = null;
                  if (q.bboxes && q.bboxes.length > 0) {
                    bbox = q.bboxes.find((b) => b.page === pNum) || q.bboxes[0];
                  } else if (q.pageNumber === pNum) {
                    bbox = q.boundingBox;
                  }

                  if (!bbox) return null;

                  return (
                    <div
                      key={`${q.id}_p${pNum}`}
                      ref={(el) => {
                        // Store primary ref for scrolling
                        if (q.pageNumber === pNum || !highlightRefs.current[q.id]) {
                          highlightRefs.current[q.id] = el;
                        }
                      }}
                      onClick={() => onSelectQuestion(q)}
                      className={`
                        absolute cursor-pointer transition-all duration-300 rounded-lg group
                        ${isSelected
                          ? 'active-answer-highlight bg-[#5DFF35]/25 border-2 border-[#3DD118] z-30 ring-4 ring-[#3DD118]/20'
                          : 'bg-[#5DFF35]/15 hover:bg-[#5DFF35]/25 border border-[#3DD118]/80 hover:border-[#3DD118] z-10'
                        }
                      `}
                      style={{
                        top: `${bbox.y}%`,
                        left: `${bbox.x}%`,
                        width: `${bbox.width}%`,
                        height: `${bbox.height}%`,
                      }}
                    >
                      {/* Floating Question Tag Pill matching Figma */}
                      <div
                        className={`
                          absolute -top-3 left-3 px-2.5 py-0.5 rounded-md text-xs font-black shadow-md flex items-center gap-1 transition-all
                          ${isSelected
                            ? 'bg-[#33AC15] text-white scale-110 ring-2 ring-white'
                            : 'bg-[#33AC15] text-white group-hover:scale-105'
                          }
                        `}
                      >
                        <span>Q{q.displayNumber || q.questionNumber}</span>
                        <span className="opacity-80 text-[10px]">
                          ({q.scoredMarks}/{q.maxMarks})
                        </span>
                      </div>

                      {/* Hover info tooltip */}
                      <div className="hidden group-hover:flex absolute bottom-1 right-1 bg-[#2F2F2F]/90 text-white text-[10px] px-2 py-0.5 rounded shadow-sm z-40 pointer-events-none whitespace-nowrap">
                        Click to inspect Q{q.displayNumber}
                      </div>
                    </div>
                  );
                })}

                {/* Render Unmatched Scribbles on this page */}
                {unmatchedOnThisPage.map((unm) => (
                  <div
                    key={unm.id}
                    className="absolute border border-dashed border-[#FF934F] bg-[#FF934F]/15 rounded-lg p-1 text-[10px] text-[#C03409] font-bold z-10 pointer-events-none"
                    style={{
                      top: `${unm.boundingBox.y}%`,
                      left: `${unm.boundingBox.x}%`,
                      width: `${unm.boundingBox.width}%`,
                      height: `${unm.boundingBox.height}%`,
                    }}
                  >
                    <span>⚠️ Unmatched scribble</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom Footer Information Banner */}
      <div className="px-4 py-2.5 bg-[#F6F6F6] border-t border-[#E5E5E5] flex items-center justify-between text-xs text-[#5D5D5D] shrink-0 select-none">
        <div className="flex items-center gap-2 truncate">
          <Info className="w-3.5 h-3.5 text-[#FF5623] shrink-0" />
          <span className="truncate">
            {selectedQuestion
              ? selectedQuestion.boundingBox
                ? `Active Highlight: Question ${selectedQuestion.displayNumber} (Page ${selectedQuestion.pageNumber})`
                : `Question ${selectedQuestion.displayNumber} was unanswered`
              : 'Click any question or green highlight region to inspect'}
          </span>
        </div>
        <div className="flex items-center gap-2 font-medium shrink-0 ml-2">
          <span>{totalMapped} mapped {totalMapped === 1 ? 'answer' : 'answers'} across {displayPages.length} {displayPages.length === 1 ? 'page' : 'pages'}</span>
        </div>
      </div>
    </div>
  );
}
