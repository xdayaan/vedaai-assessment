'use client';

import React from 'react';
import Image from 'next/image';
import {
  LayoutGrid,
  Users2,
  FileText,
  BookOpen,
  Clock,
  Sparkles,
  PanelLeftClose,
  PanelLeft,
  X,
} from 'lucide-react';

export default function Sidebar({
  isOpen = true,
  onToggle,
  isMobile = false,
  activeItem = 'Exams',
  onSelectNav,
}) {
  const navItems = [
    { name: 'Home', icon: LayoutGrid },
    { name: 'My Classroom', icon: Users2 },
    { name: 'Assignments', icon: FileText },
    { name: 'Exams', icon: BookOpen, active: true },
    { name: 'My Library', icon: Clock, badge: '32' },
  ];

  if (isMobile) {
    return (
      <>
        {/* Backdrop Overlay */}
        <div
          onClick={onToggle}
          className={`
            fixed inset-0 bg-black/40 backdrop-blur-xs z-40 transition-opacity duration-300
            ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}
          `}
        />

        {/* Mobile Drawer */}
        <aside
          className={`
            fixed top-0 bottom-0 left-0 w-[290px] bg-white z-50 shadow-2xl p-5 flex flex-col justify-between transition-transform duration-300 ease-in-out select-none
            ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          `}
        >
          {/* Top Section */}
          <div className="flex flex-col gap-5">
            {/* Brand Logo & Close Button */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 shrink-0">
                  <Image
                    src="/images/vedai_logo.svg"
                    alt="VedaAI"
                    width={40}
                    height={40}
                    className="w-10 h-10 object-contain"
                    priority
                  />
                </div>
                <span className="text-2xl font-extrabold text-[#303030] tracking-tight">
                  VedaAI
                </span>
              </div>

              <button
                onClick={onToggle}
                className="w-8 h-8 rounded-full bg-[#F6F6F6] hover:bg-[#EFEFEF] flex items-center justify-center text-[#5D5D5D] transition-colors"
                title="Close Sidebar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* AI Teacher's Toolkit Button */}
            <div className="w-full py-2.5 px-4 bg-[#272727] hover:bg-[#1f1f1f] text-white rounded-full flex items-center justify-center gap-2 text-xs font-bold border-2 border-[#FF5623]/80 shadow-xs cursor-pointer transition-all">
              <Sparkles className="w-4 h-4 text-[#FF5623] shrink-0" />
              <span>AI Teacher’s Toolkit</span>
            </div>

            {/* Navigation Menu */}
            <nav className="flex flex-col gap-1 mt-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = item.name === activeItem;

                return (
                  <button
                    key={item.name}
                    onClick={() => onSelectNav && onSelectNav(item.name)}
                    className={`
                      w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm transition-all
                      ${isActive
                        ? 'bg-[#F0F0F0] text-[#303030] font-bold'
                        : 'text-[#5E5E5E] hover:bg-[#F6F6F6] hover:text-[#303030] font-medium'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#303030]' : 'text-[#7A7A7A]'}`} />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <span className="px-2 py-0.5 rounded-md bg-[#FF5623] text-white font-bold text-xs">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Bottom Section: DPS School Card */}
          <div className="p-3 bg-[#F0F0F0] rounded-2xl flex items-center gap-3 border border-[#E0E0E0]/80">
            <div className="w-11 h-11 rounded-xl bg-white shrink-0 border border-[#D5D5D5] flex items-center justify-center p-1.5 shadow-2xs overflow-hidden">
              <Image
                src="/images/dps_emblem.png"
                alt="DPS"
                width={40}
                height={40}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex flex-col min-w-0 text-left">
              <span className="text-sm font-bold text-[#303030] tracking-tight truncate leading-tight">
                Delhi Public School
              </span>
              <span className="text-xs text-[#5E5E5E] truncate mt-0.5">
                Bokaro Steel City
              </span>
            </div>
          </div>
        </aside>
      </>
    );
  }

  // Desktop Floating Sidebar
  return (
    <aside
      className={`
        bg-white rounded-2xl shadow-md flex flex-col justify-between transition-all duration-300 shrink-0 select-none
        h-[calc(100vh-2rem)] my-4 ml-4 ${isOpen ? 'w-64 p-5' : 'w-20 p-3'}
      `}
    >
      {/* Top Section: Logo & AI Toolkit Badge */}
      <div className="flex flex-col gap-5">
        {/* Brand Logo & Collapse Toggle */}
        <div className={`flex items-center ${isOpen ? 'justify-between' : 'justify-center'}`}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 shrink-0">
              <Image
                src="/images/vedai_logo.svg"
                alt="VedaAI"
                width={40}
                height={40}
                className="w-10 h-10 object-contain"
                priority
              />
            </div>
            {isOpen && (
              <span className="text-2xl font-extrabold text-[#303030] tracking-tight">
                VedaAI
              </span>
            )}
          </div>

          {isOpen && (
            <button
              onClick={onToggle}
              className="p-1.5 text-[#7A7A7A] hover:text-[#303030] hover:bg-[#F3F3F3] rounded-lg transition-colors"
              title="Collapse Sidebar"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Collapsed expand button */}
        {!isOpen && (
          <button
            onClick={onToggle}
            className="w-full flex justify-center p-1.5 text-[#7A7A7A] hover:text-[#303030] hover:bg-[#F3F3F3] rounded-lg transition-colors"
            title="Expand Sidebar"
          >
            <PanelLeft className="w-4 h-4" />
          </button>
        )}

        {/* AI Teacher's Toolkit Pill Button */}
        {isOpen ? (
          <div className="w-full py-2.5 px-4 bg-[#272727] hover:bg-[#1f1f1f] text-white rounded-full flex items-center justify-center gap-2 text-xs font-bold border-2 border-[#FF5623]/80 shadow-xs cursor-pointer transition-all">
            <Sparkles className="w-3.5 h-3.5 text-[#FF5623] shrink-0" />
            <span className="truncate">AI Teacher’s Toolkit</span>
          </div>
        ) : (
          <div
            onClick={onToggle}
            className="w-10 h-10 mx-auto bg-[#272727] text-[#FF5623] rounded-full flex items-center justify-center border-2 border-[#FF5623]/80 cursor-pointer shadow-xs"
            title="AI Teacher’s Toolkit"
          >
            <Sparkles className="w-4 h-4" />
          </div>
        )}

        {/* Navigation Menu */}
        <nav className="flex flex-col gap-1 mt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = item.name === activeItem;

            return (
              <button
                key={item.name}
                onClick={() => onSelectNav && onSelectNav(item.name)}
                className={`
                  w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm transition-all
                  ${isActive
                    ? 'bg-[#F0F0F0] text-[#303030] font-bold'
                    : 'text-[#5E5E5E] hover:bg-[#F6F6F6] hover:text-[#303030] font-medium'
                  }
                  ${!isOpen ? 'justify-center px-0' : ''}
                `}
                title={!isOpen ? item.name : undefined}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#303030]' : 'text-[#7A7A7A]'}`} />
                  {isOpen && <span>{item.name}</span>}
                </div>
                {isOpen && item.badge && (
                  <span className="px-2 py-0.5 rounded-md bg-[#FF5623] text-white font-bold text-xs">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: School Info Card */}
      <div>
        {isOpen ? (
          <div className="p-3 bg-[#F0F0F0] rounded-2xl flex items-center gap-3 border border-[#E0E0E0]/80">
            <div className="w-11 h-11 rounded-xl bg-white shrink-0 border border-[#D5D5D5] flex items-center justify-center p-1.5 shadow-2xs overflow-hidden">
              <Image
                src="/images/dps_emblem.png"
                alt="DPS"
                width={40}
                height={40}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex flex-col min-w-0 text-left">
              <span className="text-sm font-bold text-[#303030] tracking-tight truncate leading-tight">
                Delhi Public School
              </span>
              <span className="text-xs text-[#5E5E5E] truncate mt-0.5 font-medium">
                Bokaro Steel City
              </span>
            </div>
          </div>
        ) : (
          <div
            onClick={onToggle}
            className="w-11 h-11 mx-auto rounded-xl bg-[#F0F0F0] border border-[#D0D0D0] p-1.5 flex items-center justify-center shadow-2xs cursor-pointer"
            title="Delhi Public School"
          >
            <Image
              src="/images/dps_emblem.png"
              alt="DPS"
              width={32}
              height={32}
              className="w-full h-full object-contain"
            />
          </div>
        )}
      </div>
    </aside>
  );
}
