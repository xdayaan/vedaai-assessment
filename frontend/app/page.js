'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import UploadScreen from '@/components/UploadScreen';
import LoadingScreen from '@/components/LoadingScreen';
import MappingScreen from '@/components/MappingScreen';
import GradingSummaryModal from '@/components/GradingSummaryModal';
import { SAMPLE_ASSESSMENT } from '@/data/sampleData';
import {
  uploadAssessmentFiles,
  startProcessing,
  pollAssessmentUntilComplete,
} from '@/utils/api';

export default function Home() {
  const [currentStep, setCurrentStep] = useState('upload'); // 'upload' | 'loading' | 'mapping'
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [activeNav, setActiveNav] = useState('Exams');
  const [assessmentData, setAssessmentData] = useState(SAMPLE_ASSESSMENT);
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const [liveStatus, setLiveStatus] = useState(null); // null for sample mode, { stage, progress, error } for real backend mode

  const handleStartProcessing = async (files) => {
    // Mode 1: Demo / Sample Mode
    if (files.isSample || !files.questionPaper?.rawFile || !files.answerSheet?.rawFile) {
      setLiveStatus(null);
      setAssessmentData(SAMPLE_ASSESSMENT);
      setCurrentStep('loading');
      return;
    }

    // Mode 2: Real Backend Processing Mode
    setCurrentStep('loading');
    setLiveStatus({ stage: 'rendering', progress: 10 });

    try {
      // 1. Upload files to FastAPI backend
      const uploadRes = await uploadAssessmentFiles(
        files.questionPaper.rawFile,
        files.answerSheet.rawFile
      );
      const assessmentId = uploadRes.assessment_id;

      // 2. Trigger asynchronous background processing
      await startProcessing(assessmentId);

      // 3. Poll for status until completed
      const realResult = await pollAssessmentUntilComplete(
        assessmentId,
        (stat) => {
          setLiveStatus(stat);
        }
      );

      // 4. Update assessment state with real backend result
      setAssessmentData(realResult);
      setCurrentStep('mapping');
      setLiveStatus(null);
    } catch (err) {
      console.error('Backend processing error:', err);
      setLiveStatus({
        stage: 'failed',
        progress: 0,
        error: `Processing error: ${err.message || 'Could not connect to FastAPI backend at http://localhost:8000'}. You can also use "Try with Sample Assignment".`,
      });
    }
  };

  const handleLoadingComplete = () => {
    setCurrentStep('mapping');
  };

  const handleBackToUpload = () => {
    setLiveStatus(null);
    setCurrentStep('upload');
  };

  const handleReset = () => {
    setLiveStatus(null);
    setAssessmentData(SAMPLE_ASSESSMENT);
    setCurrentStep('upload');
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gradient-to-b from-[#F5F5F5] to-[#E9E5E5] select-none">
      {/* Desktop Floating Sidebar */}
      <div className="hidden lg:block shrink-0">
        <Sidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          activeItem={activeNav}
          onSelectNav={setActiveNav}
        />
      </div>

      {/* Mobile Drawer Sidebar */}
      <div className="lg:hidden">
        <Sidebar
          isOpen={mobileSidebarOpen}
          onToggle={() => setMobileSidebarOpen(!mobileSidebarOpen)}
          isMobile={true}
          activeItem={activeNav}
          onSelectNav={(item) => {
            setActiveNav(item);
            setMobileSidebarOpen(false);
          }}
        />
      </div>

      {/* Right Column: Floating Header + Main Canvas */}
      <div className="flex-1 flex flex-col h-full overflow-hidden p-3 sm:p-4 gap-3 sm:gap-4 min-w-0">
        {/* Top Floating Navigation Bar */}
        <Navbar
          currentStep={currentStep}
          onBack={handleBackToUpload}
          onOpenSummary={() => setIsSummaryOpen(true)}
          onToggleSidebar={() => setMobileSidebarOpen(true)}
          onReset={handleReset}
        />

        {/* Dynamic View Canvas */}
        <main className="flex-1 overflow-y-auto flex flex-col relative min-h-0">
          {currentStep === 'upload' && (
            <UploadScreen
              onStartProcessing={handleStartProcessing}
              onLoadSample={() => {
                setLiveStatus(null);
                setAssessmentData(SAMPLE_ASSESSMENT);
                setCurrentStep('loading');
              }}
            />
          )}

          {currentStep === 'loading' && (
            <LoadingScreen
              onComplete={handleLoadingComplete}
              liveStatus={liveStatus}
              onCancel={handleBackToUpload}
            />
          )}

          {currentStep === 'mapping' && (
            <MappingScreen
              assessmentData={assessmentData}
              onOpenSummary={() => setIsSummaryOpen(true)}
            />
          )}
        </main>
      </div>

      {/* Grading Summary Modal */}
      <GradingSummaryModal
        isOpen={isSummaryOpen}
        onClose={() => setIsSummaryOpen(false)}
        assessmentData={assessmentData}
        questions={assessmentData.questions}
      />
    </div>
  );
}
