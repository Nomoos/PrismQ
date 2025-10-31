# Quick Reference - What To Do Next

**Last Updated**: 2025-10-31

---

## 🚀 START HERE - Immediate Action Items

### For Backend Developers

**Issue #104: Log Streaming** 
- **Status**: Ready to start NOW
- **Estimated**: 1-2 weeks
- **Location**: `_meta/issues/new/104-log-streaming.md`
- **Dependencies**: #103 ✅ (Complete)
- **Can work in parallel with**: #105, #106

**Issue #106: Parameter Persistence**
- **Status**: Ready to start NOW  
- **Estimated**: 1 week
- **Location**: `_meta/issues/new/106-parameter-persistence.md`
- **Dependencies**: #103 ✅ (Complete)
- **Can work in parallel with**: #104, #105

---

### For Frontend Developers

**Issue #105: Frontend Module UI**
- **Status**: Ready to start NOW
- **Estimated**: 2-3 weeks
- **Location**: `_meta/issues/new/105-frontend-module-ui.md`
- **Dependencies**: #101 ✅, #102 ✅ (Complete)
- **Can work in parallel with**: #104, #106

---

### For Full Stack Developers

**Pick based on backend/frontend preference**:
- Backend heavy: Start with #104 or #106
- Frontend heavy: Start with #105
- Balanced: Start with #105, then move to #108

---

### For Source Integration Developers

**Signals Sources** (12 remaining)
- **Status**: Can start ANY TIME (independent work)
- **Estimated**: 3-5 days per source
- **Location**: `Sources/Signals/` directory
- **Reference**: `Sources/Signals/Trends/GoogleTrends/` (completed example)
- **Master Plan**: `_meta/issues/done/027-source-implementation-master-plan.md`

**Available Sources to Implement**:
1. TrendsFileSource (Trends subcategory)
2. TikTokHashtagSource (Hashtags)
3. InstagramHashtagSource (Hashtags)  
4. TikTokSoundsSource (Sounds)
5. InstagramAudioTrendsSource (Sounds)
6. MemeTrackerSource (Memes)
7. KnowYourMemeSource (Memes)
8. SocialChallengeSource (Challenges)
9. GeoLocalTrendsSource (Geo-Local)
10. NewsAPISource (News)
11. GoogleNewsSource (News)
12. [One additional source TBD]

**Choose any source - they're all independent!**

---

## 📊 Current Project Status

### ✅ Completed
- Client Module Foundation (#101, #102, #103)
- 27 of 38 sources implemented
- All Content/Commerce/Events/Community/Creative/Internal sources done

### 🚧 In Progress  
- Nothing currently in WIP (ready for new work!)

### ⏳ Next Up (High Priority)
- #104: Log Streaming
- #105: Frontend Module UI  
- #106: Parameter Persistence
- Remaining Signals Sources (12)

### 🔮 Future (Medium Priority)
- #107: Live Logs UI (Week 3-4)
- #108: Concurrent Runs (Week 3-4)
- #109: Error Handling (Week 5-6)
- #110: Integration (Week 7-8)
- #111: Testing (Week 7-8)
- #112: Documentation (Week 7-8)

---

## 📋 Issue Locations Quick Map

```
_meta/issues/
├── new/           ← Issues ready to start (#104-#112)
├── wip/           ← Move here when you start working
├── done/          ← Move here when complete (#101-#103 are here)
└── backlog/       ← Future work (#001-#010)
```

---

## 🎯 How to Start Working

### 1. Pick an Issue
Choose from the "START HERE" section above based on your skills.

### 2. Move Issue to WIP
```bash
cd _meta/issues/
mv new/[issue-number]-*.md wip/
```

### 3. Update Issue Status
Edit the file and change:
```markdown
**Status**: New
```
to:
```markdown
**Status**: In Progress
```

### 4. Read Full Issue Details
Open the issue file and read all requirements.

### 5. Create Feature Branch
```bash
git checkout -b feature/[issue-number]-brief-description
```

### 6. Implement Following SOLID Principles
See `.github/copilot-instructions.md` for coding guidelines.

### 7. Test Your Changes
Aim for >80% code coverage.

### 8. Move to Done When Complete
```bash
cd _meta/issues/
mv wip/[issue-number]-*.md done/
```

---

## 💡 Parallelization Strategy

### This Week (Week 1-2)

**Can work simultaneously:**
```
Developer #1: #104 (Backend - Log Streaming)
Developer #2: #106 (Backend - Parameter Persistence)  
Developer #3: #105 (Frontend - Module UI)
Developer #4+: Any Signals Source
```

**These issues are INDEPENDENT and don't conflict!**

---

## 📚 Key Documentation

### Must Read
1. **NEXT_STEPS.md** - Full detailed plan (this file's parent)
2. **IMPLEMENTATION_TIMELINE.md** - Visual timeline and dependencies
3. **ROADMAP.md** - Overall project roadmap

### Reference
- **WEB_CLIENT_SUMMARY.md** - Web client overview
- **027-source-implementation-master-plan.md** - Source implementation guide
- **.github/copilot-instructions.md** - Coding standards

### For Specific Issues
- Issue files in `_meta/issues/new/` for detailed requirements

---

## ⚡ Quick Wins (Can Complete in 1 Week)

1. **#106: Parameter Persistence** - ~5-7 days
2. **Any Signals Source** - ~3-5 days each
3. **Documentation updates** - ~2-3 days

Start with these if you want to deliver value quickly!

---

## 🔥 Critical Path (Must Be Sequential)

```
#104 → #107 → #110
```

**DO NOT SKIP** - #107 needs #104 complete, #110 needs #107 complete.

---

## 🤝 Coordination Points

### Week 2 Checkpoint
- Check if #104, #105, #106 are progressing
- Coordinate on any blockers
- Plan Week 3-4 work

### Week 4 Checkpoint  
- Ensure #105 is complete (needed for #107)
- Ensure #104 is complete (needed for #107)
- Plan #107 and #108 start

### Week 6 Checkpoint
- Review #107 and #108 completion
- Plan final integration (#110)

### Week 8 Checkpoint
- Verify all issues complete
- Plan Phase 1 work (#001, #002)

---

## 📞 Who to Ask

### Technical Questions
- Backend: Check `Client/Backend/` existing code
- Frontend: Check `Client/Frontend/` existing code  
- Sources: Reference `Sources/Signals/Trends/GoogleTrends/`

### Process Questions
- Issue workflow: See `_meta/issues/README.md`
- Contribution guide: See `_meta/docs/CONTRIBUTING.md`

---

## 🎓 Learning Resources

### FastAPI (Backend)
- Official Docs: https://fastapi.tiangolo.com/
- SSE Example: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse

### Vue 3 (Frontend)  
- Official Docs: https://vuejs.org/
- Composition API: https://vuejs.org/guide/extras/composition-api-faq.html

### TypeScript
- Handbook: https://www.typescriptlang.org/docs/handbook/intro.html

### Testing
- Pytest: https://docs.pytest.org/
- Vitest: https://vitest.dev/
- Playwright: https://playwright.dev/

---

## ✅ Daily Checklist

### Starting Your Day
- [ ] Pull latest changes from main
- [ ] Check if your WIP issue still has no blockers
- [ ] Review any comments on your PR (if active)

### During Development
- [ ] Follow SOLID principles
- [ ] Write tests as you code (TDD)
- [ ] Commit frequently with clear messages
- [ ] Push to remote at least once per day

### Before Ending Day
- [ ] Ensure all tests pass
- [ ] Push latest changes
- [ ] Update issue status if needed
- [ ] Note any blockers for tomorrow

---

## 🚨 Common Pitfalls to Avoid

1. **Don't start #107 before #104 is done** - Hard dependency
2. **Don't skip writing tests** - Requirement is >80% coverage
3. **Don't work in main branch** - Always use feature branches
4. **Don't forget to update issue status** - Keep WIP folder current
5. **Don't implement features not in the issue** - Stick to requirements (YAGNI)

---

## 📈 Success Metrics

### For Issues #104-#106 (Week 1-2)
- [ ] All three can run concurrently
- [ ] Log streaming works with real-time updates
- [ ] Parameters save and load correctly
- [ ] Frontend displays all modules

### For Complete Client Module (Week 8)
- [ ] Can launch any PrismQ module from UI
- [ ] See real-time logs streaming
- [ ] Run 10+ modules concurrently
- [ ] Parameters persist across sessions
- [ ] >80% test coverage
- [ ] Complete documentation

---

## 🎯 This Week's Focus

```
PRIMARY GOAL: Complete #104, #105, #106
STRETCH GOAL: Implement 2-4 Signals sources
```

**By end of Week 2:**
- Backend has log streaming working
- Backend has parameter persistence working  
- Frontend has dashboard and launch UI working
- 2+ additional Signals sources implemented

---

## 🔗 Quick Links

- **Repository**: https://github.com/Nomoos/PrismQ.IdeaInspiration
- **Issues**: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues
- **Client Backend**: `/Client/Backend/`
- **Client Frontend**: `/Client/Frontend/`
- **Sources**: `/Sources/`

---

**Need Help?**
1. Read the full issue details in `_meta/issues/new/[issue].md`
2. Check existing code for patterns
3. Review NEXT_STEPS.md for detailed information
4. Ask in GitHub Issues if stuck

---

**Last Updated**: 2025-10-31  
**Next Review**: Start of Week 2
