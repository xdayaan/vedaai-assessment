'use client';

import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Sparkles, FileSearch, Layers, Brain, AlertCircle } from 'lucide-react';

export default function LoadingScreen({ onComplete, liveStatus = null, onCancel }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(15);

  const steps = [
    {
      title: 'Extracting questions in printed order',
      desc: 'Preserving hierarchy, sub-parts 11(a) and 11(b), and question numbering',
      icon: FileSearch,
    },
    {
      title: 'Scanning student handwritten answers',
      desc: 'Transcribing text, diagrams, and detecting answer layout',
      icon: Layers,
    },
    {
      title: 'Mapping answers to questions',
      desc: 'Identifying exact coordinates, bounding boxes & multi-page spans',
      icon: Loader2,
    },
    {
      title: 'Generating AI grading & feedback',
      desc: 'Calculating scores against rubric & providing formative advice',
      icon: Brain,
    },
  ];

  // Mode 1: Simulated progression for Demo/Sample Mode (when liveStatus is null)
  useEffect(() => {
    if (liveStatus) return; // In real mode, driven by liveStatus

    const timer1 = setTimeout(() => {
      setCurrentStep(1);
      setProgress(40);
    }, 1200);

    const timer2 = setTimeout(() => {
      setCurrentStep(2);
      setProgress(70);
    }, 2400);

    const timer3 = setTimeout(() => {
      setCurrentStep(3);
      setProgress(95);
    }, 3600);

    const timer4 = setTimeout(() => {
      setProgress(100);
      onComplete();
    }, 4500);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, [onComplete, liveStatus]);

  // Mode 2: Live Backend Progression
  useEffect(() => {
    if (!liveStatus) return;

    if (liveStatus.progress !== undefined) {
      setProgress(liveStatus.progress);
    }

    const stage = liveStatus.stage;
    if (stage === 'rendering') {
      setCurrentStep(0);
    } else if (stage === 'question_extraction') {
      setCurrentStep(1);
    } else if (stage === 'answer_extraction') {
      setCurrentStep(2);
    } else if (stage === 'mapping') {
      setCurrentStep(3);
    } else if (stage === 'completed') {
      setCurrentStep(4);
      setProgress(100);
    }
  }, [liveStatus]);

  return (
    <div className="w-full flex-1 flex flex-col items-center justify-center p-4 md:p-8 relative select-none">
      {/* Background Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#FF5623] opacity-[0.07] blur-[100px] pointer-events-none rounded-full" />

      <div className="w-full max-w-2xl bg-white rounded-3xl p-6 md:p-10 shadow-card border border-[#E5E5E5] flex flex-col items-center text-center gap-8 z-10">
        {/* Animated Custom Loader matching Figma */}
        <div className="relative w-36 h-36 flex items-center justify-center">
          {/* Concentric rotating glowing arcs */}
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-[#FF5623] border-r-[#FF5623]/60 animate-spin" />
          <div className="absolute inset-3 rounded-full border-2 border-transparent border-b-[#FF934F] border-l-[#FF934F]/40 animate-[spin_3s_linear_infinite_reverse]" />
          <div className="absolute inset-6 rounded-full border border-dashed border-[#FF5623]/50 animate-pulse" />

          {/* Central Pulsating Core */}
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#FF5623] to-[#FF934F] shadow-glow-orange flex items-center justify-center text-white">
            <Sparkles className="w-7 h-7 animate-bounce" />
          </div>
        </div>

        {/* Text Header matching Figma */}
        <div className="flex flex-col items-center gap-1">
          <h2 className="text-2xl md:text-3xl font-bold text-[#2F2F2F] tracking-tight">
            {liveStatus?.error ? 'Processing Failed' : 'Extracting...'}
          </h2>
          <p className="text-base text-[#5D5D5D] font-normal">
            {liveStatus?.error ? liveStatus.error : 'This may take a while'}
          </p>
        </div>

        {liveStatus?.error && onCancel && (
          <button
            onClick={onCancel}
            className="px-5 py-2 bg-[#2F2F2F] text-white rounded-xl font-bold text-xs hover:bg-black transition-colors"
          >
            Back to Upload
          </button>
        )}

        {/* Dynamic Progress Bar */}
        <div className="w-full max-w-md flex flex-col gap-2">
          <div className="w-full h-2 bg-[#EFEFEF] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#FF5623] to-[#FF934F] rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-[#A9A9A9] font-medium">
            <span>AI Vision Engine v2.5</span>
            <span>{progress}% Completed</span>
          </div>
        </div>

        {/* Step-by-Step Progress List */}
        <div className="w-full max-w-md flex flex-col gap-3 text-left">
          {steps.map((step, idx) => {
            const isDone = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div
                key={idx}
                className={`
                  p-3 rounded-xl border transition-all flex items-start gap-3
                  ${isCurrent
                    ? 'bg-[#FFF6E5] border-[#FFD8A8] shadow-xs'
                    : isDone
                    ? 'bg-[#F9FDF8] border-[#D4F2CA]'
                    : 'bg-[#FAFAFA] border-[#EAEAEA] opacity-60'
                  }
                `}
              >
                <div className="mt-0.5 shrink-0">
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-[#33AC15]" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-[#FF5623] animate-spin" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-[#CDCDCD]" />
                  )}
                </div>
                <div className="flex flex-col min-w-0">
                  <span
                    className={`
                      text-xs font-bold
                      ${isCurrent ? 'text-[#FF5623]' : isDone ? 'text-[#2F2F2F]' : 'text-[#5D5D5D]'}
                    `}
                  >
                    {step.title}
                  </span>
                  <span className="text-[11px] text-[#7A7A7A] truncate">
                    {step.desc}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
