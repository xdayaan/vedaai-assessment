'use client';

import React from 'react';
import Image from 'next/image';
import {
  ArrowLeft,
  Bell,
  ChevronDown,
  BookOpen,
  Menu,
} from 'lucide-react';

export default function Navbar({
  currentStep,
  onBack,
  onOpenSummary,
  onToggleSidebar,
  studentName = 'Madhur Rastogi',
}) {
  return (
    <header className="w-full bg-white shadow-md rounded-2xl px-4 md:px-6 py-3 flex items-center justify-between z-30 shrink-0 select-none">
      {/* ================= DESKTOP HEADER (>= lg) ================= */}
      <div className="hidden lg:flex items-center gap-3">
        {/* Desktop Back button */}
        <button
          onClick={onBack}
          className="w-9 h-9 rounded-full bg-[#FFFFFF] hover:bg-[#F3F3F3] border border-[#E5E5E5] flex items-center justify-center text-[#303030] transition-colors shadow-2xs"
          title="Go back"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>

        {/* Breadcrumbs: Exams */}
        <div className="flex items-center gap-2 text-sm">
          <div className="flex items-center gap-1.5 text-[#303030] font-bold">
            <BookOpen className="w-4 h-4 text-[#7A7A7A]" />
            <span className="text-base font-semibold text-[#303030]">Exams</span>
          </div>
          {currentStep === 'mapping' && (
            <>
              <span className="text-[#A9A9A9]">/</span>
              <span className="text-[#FF5623] font-semibold">
                Assessment Mapping & Grading
              </span>
            </>
          )}
        </div>
      </div>

      {/* ================= MOBILE HEADER (< lg) ================= */}
      {/* Left: Back Arrow + Official Logo + VedaAI title */}
      <div className="lg:hidden flex items-center gap-2.5">
        <button
          onClick={onBack}
          className="p-1 -ml-1 text-[#1D1B20] hover:bg-[#F3F3F3] rounded-lg transition-colors"
          title="Back"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-7 h-7 shrink-0">
          <Image
            src="/images/vedai_logo.svg"
            alt="VedaAI"
            width={28}
            height={28}
            className="w-7 h-7 object-contain"
            priority
          />
        </div>
        <span className="text-xl font-extrabold text-[#303030] tracking-tight">
          VedaAI
        </span>
      </div>

      {/* ================= RIGHT SIDE ACTIONS ================= */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Help '?' Button - Desktop Only matching Figma */}
        <button
          onClick={() => alert('VedaAI Assessment Mapper\n\n1. Upload Question Paper & Student Answer Sheet.\n2. Extracted questions and answer regions are automatically mapped.\n3. Click on any question to view its exact highlighted region on the sheet.\n4. Teacher can modify scores and feedback at any time.')}
          className="hidden lg:flex w-9 h-9 rounded-full bg-[#F6F6F6] hover:bg-[#EFEFEF] items-center justify-center text-[#303030] font-bold text-sm transition-colors"
          title="Help & Guidelines"
        >
          ?
        </button>

        {/* Notifications Bell with Orange Dot (Desktop & Mobile) */}
        <button
          className="relative w-9 h-9 rounded-full bg-[#F6F6F6] hover:bg-[#EFEFEF] flex items-center justify-center text-[#303030] transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4 text-[#303030]" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-[#FF5623] rounded-full ring-2 ring-white" />
        </button>

        {/* 4-Point Star Sparkle Icon - Desktop Only matching Figma */}
        <div className="hidden lg:flex w-9 h-9 rounded-full bg-[#F6F6F6] items-center justify-center text-[#2B2B2B]">
          <span className="text-sm leading-none font-bold">✦</span>
        </div>

        {/* User Profile Chip - Desktop Only matching Figma */}
        <div className="hidden lg:flex items-center gap-2 pl-1.5 pr-2.5 py-1 bg-white hover:bg-[#F9F9F9] rounded-xl border border-[#EAEAEA] cursor-pointer transition-colors shadow-2xs">
          <div className="w-7 h-7 rounded-full overflow-hidden relative bg-[#F6F6F6] border border-[#E0E0E0] shrink-0">
            <Image
              src="/images/madhur_avatar.png"
              alt="Madhur Rastogi"
              width={28}
              height={28}
              className="object-cover w-full h-full"
            />
          </div>
          <span className="text-sm font-semibold text-[#303030]">
            {studentName}
          </span>
          <ChevronDown className="w-3.5 h-3.5 text-[#5D5D5D]" />
        </div>

        {/* Mobile User Avatar Circle (32x32) */}
        <div className="lg:hidden w-8 h-8 rounded-full overflow-hidden relative bg-[#F6F6F6] border border-[#E0E0E0] shrink-0">
          <Image
            src="/images/mobile_avatar.png"
            alt="User"
            width={32}
            height={32}
            className="object-cover w-full h-full"
          />
        </div>

        {/* Mobile Hamburger Menu Button - (< lg) */}
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-1.5 text-[#1D1B20] hover:bg-[#F3F3F3] rounded-lg transition-colors cursor-pointer"
          title="Open Navigation Menu"
          aria-label="Open Navigation Menu"
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>
    </header>
  );
}
