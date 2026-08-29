'use client';

import React, { useRef, useState } from 'react';
import Image from 'next/image';
import {
  Upload as UploadIcon,
  ArrowRight,
  X,
  Sparkles,
  CheckSquare,
  Zap,
  Clock,
  Settings as SettingsIcon,
} from 'lucide-react';

export default function UploadScreen({
  onStartProcessing,
  onLoadSample,
}) {
  const [questionPaperFile, setQuestionPaperFile] = useState(null);
  const [answerSheetFile, setAnswerSheetFile] = useState(null);
  const [isDraggingQP, setIsDraggingQP] = useState(false);
  const [isDraggingAS, setIsDraggingAS] = useState(false);

  const qpInputRef = useRef(null);
  const asInputRef = useRef(null);

  const handleQPUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setQuestionPaperFile({
        name: file.name,
        size: `${(file.size / (1024 * 1024)).toFixed(1)}MB`,
        pages: '2 Pages',
        rawFile: file,
      });
    }
  };

  const handleASUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setAnswerSheetFile({
        name: file.name,
        size: `${(file.size / (1024 * 1024)).toFixed(1)}MB`,
        pages: '4 Pages',
        rawFile: file,
      });
    }
  };

  const loadSampleFiles = () => {
    setQuestionPaperFile({
      name: 'Class_10_maths_unit_test.pdf',
      size: '2MB',
      pages: '2 Pages',
      isSample: true,
    });
    setAnswerSheetFile({
      name: 'student_1_answer_sheet.pdf',
      size: '8MB',
      pages: '6 Pages',
      isSample: true,
    });
  };

  const bothFilesUploaded = Boolean(questionPaperFile && answerSheetFile);

  const handleSubmit = () => {
    if (bothFilesUploaded) {
      onStartProcessing({
        questionPaper: questionPaperFile,
        answerSheet: answerSheetFile,
      });
    }
  };

  return (
    <div className="w-full flex-1 flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 relative select-none">
      <div className="w-full max-w-4xl flex flex-col items-center gap-6 sm:gap-7 z-10 my-auto">
        
        {/* Title Header matching Figma 100% */}
        <div className="text-center flex flex-col items-center gap-1.5 w-full">
          {/* Desktop Title - Single line, no wrapping */}
          <div className="hidden sm:flex items-center justify-center gap-2 sm:gap-3 text-2xl sm:text-3xl lg:text-[40px] font-bold tracking-tight text-[#2B2B2B] whitespace-nowrap">
            <span className="shrink-0">Upload</span>
            <div className="px-3 sm:px-3.5 py-0.5 sm:py-1 bg-[#FF9350]/15 text-[#FF5623] rounded-lg inline-flex items-center font-bold whitespace-nowrap shrink-0">
              <span className="whitespace-nowrap">Question Paper & Answer Sheets</span>
            </div>
          </div>

          {/* Mobile Title (Stacked exactly matching Figma phone frame) */}
          <div className="sm:hidden flex flex-col items-center text-center text-[24px] font-bold text-[#2B2B2B] leading-tight whitespace-nowrap">
            <span>Upload Question Paper</span>
            <span>& Answer Sheets</span>
          </div>

          <p className="text-sm sm:text-base md:text-[20px] text-[#303030] font-normal whitespace-nowrap">
            Upload both files to get started
          </p>
        </div>

        {/* Hero Avatar Center Hub matching Figma 100% */}
        <div className="relative w-32 h-32 sm:w-36 sm:h-36 flex items-center justify-center">
          {/* Outer soft peach/orange concentric circles matching Figma Ellipse 6 & 7 */}
          <div className="absolute inset-0 rounded-full bg-[#FF5623]/10" />
          <div className="absolute inset-2.5 sm:inset-3 rounded-full bg-[#FF5623]/25" />

          {/* Center 3D Teacher Avatar Image */}
          <div className="relative w-20 h-20 sm:w-24 sm:h-24 rounded-full overflow-hidden bg-white flex items-center justify-center shadow-xs">
            <Image
              src="/images/hero_preview.png"
              alt="Teacher Avatar"
              width={96}
              height={96}
              className="object-contain w-full h-full scale-105"
              priority
            />
          </div>

          {/* 4 Orbiting Satellite Orange Badges */}
          {/* Top Left: Task Square */}
          <div className="absolute top-1 left-1.5 sm:top-2 sm:left-2 w-5 h-5 rounded-full bg-gradient-to-tr from-[#FF5623] to-[#FF8C35] text-white flex items-center justify-center shadow-xs border border-white/80">
            <CheckSquare className="w-2.5 h-2.5" />
          </div>
          {/* Top Right: Lightning */}
          <div className="absolute top-2 -right-0.5 sm:top-3 sm:right-0 w-5 h-5 rounded-full bg-gradient-to-tr from-[#FF5623] to-[#FF8C35] text-white flex items-center justify-center shadow-xs border border-white/80">
            <Zap className="w-2.5 h-2.5" />
          </div>
          {/* Bottom Left: Clock */}
          <div className="absolute -bottom-0.5 left-4 sm:bottom-0 sm:left-5 w-5 h-5 rounded-full bg-gradient-to-tr from-[#FF5623] to-[#FF8C35] text-white flex items-center justify-center shadow-xs border border-white/80">
            <Clock className="w-2.5 h-2.5" />
          </div>
          {/* Bottom Right: Settings */}
          <div className="absolute bottom-3 -right-0.5 sm:bottom-4 sm:right-0 w-5 h-5 rounded-full bg-gradient-to-tr from-[#FF5623] to-[#FF8C35] text-white flex items-center justify-center shadow-xs border border-white/80">
            <SettingsIcon className="w-2.5 h-2.5" />
          </div>
        </div>

        {/* Dual Upload Cards Container (Directly on canvas with no outer wrapper background) */}
        <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          
          {/* Card 1: Question Paper */}
          <div
            onClick={() => {
              if (!questionPaperFile) {
                qpInputRef.current?.click();
              }
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDraggingQP(true);
            }}
            onDragLeave={() => setIsDraggingQP(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDraggingQP(false);
              const file = e.dataTransfer.files?.[0];
              if (file) {
                setQuestionPaperFile({
                  name: file.name,
                  size: `${(file.size / (1024 * 1024)).toFixed(1)}MB`,
                  pages: file.type.includes('image') ? '1 Page' : 'Document',
                  rawFile: file,
                  isSample: false,
                });
              }
            }}
            className={`
              relative min-h-[140px] sm:min-h-[180px] rounded-[20px] border-[1.5px] border-dashed transition-all p-4 sm:p-6 flex flex-col items-center justify-center text-center shadow-xs
              ${questionPaperFile
                ? 'bg-white border-[#CECECE]'
                : isDraggingQP
                ? 'bg-[#FFF6E5] border-[#FF5623] scale-[1.02] cursor-pointer'
                : 'bg-white hover:bg-[#FAFAFA] border-[#CECECE] hover:border-[#A0A0A0] cursor-pointer'
              }
            `}
          >
            <input
              ref={qpInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*"
              onClick={(e) => {
                e.target.value = '';
              }}
              onChange={handleQPUpload}
              className="hidden"
            />

            {questionPaperFile ? (
              /* Filled State matching Figma 1:8797 */
              <div
                onClick={(e) => e.stopPropagation()}
                className="relative w-full max-w-[300px]"
              >
                {/* Delete 'X' button at top-right of inner card */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setQuestionPaperFile(null);
                  }}
                  className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[#2B2B2B]/90 hover:bg-black text-white flex items-center justify-center transition-colors shadow-xs z-10 cursor-pointer"
                  title="Remove file"
                >
                  <X className="w-3.5 h-3.5" />
                </button>

                <div className="w-full bg-[#F6F6F6] rounded-xl p-3 flex items-center gap-3 border border-[#EAEAEA]">
                  <div className="w-9 h-10 relative shrink-0">
                    <Image
                      src="/images/pdf_icon.png"
                      alt="PDF"
                      width={36}
                      height={40}
                      className="object-contain w-full h-full"
                    />
                  </div>
                  <div className="flex flex-col text-left min-w-0">
                    <span className="text-xs sm:text-sm font-bold text-[#2B2B2B] truncate">
                      {questionPaperFile.name}
                    </span>
                    <div className="flex items-center gap-1.5 text-xs text-[#5E5E5E]/80 mt-0.5 font-medium">
                      <span>{questionPaperFile.size}</span>
                      <span className="w-1 h-1 bg-[#5E5E5E]/80 rounded-full" />
                      <span>{questionPaperFile.pages}</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              /* Empty State matching Figma 1:8744 */
              <div className="w-full h-full flex flex-col items-center justify-center cursor-pointer gap-2 sm:gap-3 pointer-events-none">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-[#F3F3F3] flex items-center justify-center text-[#303030] transition-colors">
                  <UploadIcon className="w-5 h-5 text-[#303030]" />
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm sm:text-[18px] md:text-[20px] font-semibold sm:font-bold text-[#303030] whitespace-nowrap">
                    Upload <span className="text-[#FF5623]">Question Paper</span>
                  </span>
                  <span className="text-xs sm:text-sm text-[#5E5E5E]/60 font-normal whitespace-nowrap">
                    Max 10MB
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Card 2: Student Answer Sheet */}
          <div
            onClick={() => {
              if (!answerSheetFile) {
                asInputRef.current?.click();
              }
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDraggingAS(true);
            }}
            onDragLeave={() => setIsDraggingAS(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDraggingAS(false);
              const file = e.dataTransfer.files?.[0];
              if (file) {
                setAnswerSheetFile({
                  name: file.name,
                  size: `${(file.size / (1024 * 1024)).toFixed(1)}MB`,
                  pages: file.type.includes('image') ? '1 Page' : 'Document',
                  rawFile: file,
                  isSample: false,
                });
              }
            }}
            className={`
              relative min-h-[140px] sm:min-h-[180px] rounded-[20px] border-[1.5px] border-dashed transition-all p-4 sm:p-6 flex flex-col items-center justify-center text-center shadow-xs
              ${answerSheetFile
                ? 'bg-white border-[#CECECE]'
                : isDraggingAS
                ? 'bg-[#FFF6E5] border-[#FF5623] scale-[1.02] cursor-pointer'
                : 'bg-white hover:bg-[#FAFAFA] border-[#CECECE] hover:border-[#A0A0A0] cursor-pointer'
              }
            `}
          >
            <input
              ref={asInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*"
              onClick={(e) => {
                e.target.value = '';
              }}
              onChange={handleASUpload}
              className="hidden"
            />

            {answerSheetFile ? (
              /* Filled State matching Figma 1:8797 */
              <div
                onClick={(e) => e.stopPropagation()}
                className="relative w-full max-w-[300px]"
              >
                {/* Delete 'X' button at top-right of inner card */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setAnswerSheetFile(null);
                  }}
                  className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[#2B2B2B]/90 hover:bg-black text-white flex items-center justify-center transition-colors shadow-xs z-10 cursor-pointer"
                  title="Remove file"
                >
                  <X className="w-3.5 h-3.5" />
                </button>

                <div className="w-full bg-[#F6F6F6] rounded-xl p-3 flex items-center gap-3 border border-[#EAEAEA]">
                  <div className="w-9 h-10 relative shrink-0">
                    <Image
                      src="/images/pdf_icon.png"
                      alt="PDF"
                      width={36}
                      height={40}
                      className="object-contain w-full h-full"
                    />
                  </div>
                  <div className="flex flex-col text-left min-w-0">
                    <span className="text-xs sm:text-sm font-bold text-[#2B2B2B] truncate">
                      {answerSheetFile.name}
                    </span>
                    <div className="flex items-center gap-1.5 text-xs text-[#5E5E5E]/80 mt-0.5 font-medium">
                      <span>{answerSheetFile.size}</span>
                      <span className="w-1 h-1 bg-[#5E5E5E]/80 rounded-full" />
                      <span>{answerSheetFile.pages}</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              /* Empty State matching Figma 1:8744 */
              <div className="w-full h-full flex flex-col items-center justify-center cursor-pointer gap-2 sm:gap-3 pointer-events-none">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-[#F3F3F3] flex items-center justify-center text-[#303030] transition-colors">
                  <UploadIcon className="w-5 h-5 text-[#303030]" />
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm sm:text-[18px] md:text-[20px] font-semibold sm:font-bold text-[#303030] whitespace-nowrap">
                    Upload <span className="text-[#FF5623]">Answer Sheet</span>
                  </span>
                  <span className="text-xs sm:text-sm text-[#5E5E5E]/60 font-normal whitespace-nowrap">
                    Max 10MB
                  </span>
                </div>
              </div>
            )}
          </div>

        </div>

        {/* Quick Sample Button for convenience */}
        <button
          onClick={loadSampleFiles}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#FFF0E8] hover:bg-[#FFE0D1] text-[#FF5623] font-bold text-xs border border-[#FFD2BE] transition-all shadow-2xs cursor-pointer -mt-2"
        >
          <Sparkles className="w-3.5 h-3.5 text-[#FF5623]" />
          <span>Try with Sample Assignment</span>
        </button>

        {/* Bottom CTA Action Bar matching Figma Frame 1984078309 100% */}
        <div className="flex flex-col items-center gap-3 text-center">
          <button
            onClick={handleSubmit}
            disabled={!bothFilesUploaded}
            className={`
              px-6 py-2.5 rounded-full font-medium text-sm flex items-center gap-2 transition-all border-2 border-white
              ${bothFilesUploaded
                ? 'bg-[#303030] hover:bg-black text-white cursor-pointer shadow-md hover:scale-[1.02]'
                : 'bg-[#303030]/60 text-white/90 cursor-not-allowed'
              }
            `}
          >
            <span>Start Mapping</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <p className="text-xs sm:text-sm text-[#5E5E5E]/80 max-w-md font-normal leading-relaxed">
            Once both files are uploaded, you’ll able to map answers with questions
          </p>
        </div>

      </div>
    </div>
  );
}
