# Critical Fixes Needed Before Deployment

**Status:** 🔴 **BLOCKING ISSUES FOUND**  
**Priority:** **IMMEDIATE**  
**Date:** December 17, 2025

---

## 🚨 Critical Issue #1: claude-agent-sdk Package Dependency

### Problem

The entire refactor depends on `claude-agent-sdk` package which:
1. **Is not installed** in the current environment
2. **May not be publicly available** on PyPI
3. **Will cause import errors** on all agent files

### Impact

- ❌ **All agents will fail** at import time
- ❌ **Examples won't run**
- ❌ **Streamlit app won't work**
- ❌ **Cannot test or deploy**

### Evidence

```python
# From base_agent.py line 11:
from claude_agent_sdk import query, ClaudeAgentOptions
```

```bash
$ pip3 list | grep claude
# No results - package not installed
```

### Resolution Options

#### Option 1: Use Anthropic SDK (RECOMMENDED)

The actual Anthropic Python SDK package is `anthropic`, not `claude-agent-sdk`. We need to update imports:

```python
# Change from:
from claude_agent_sdk import query, ClaudeAgentOptions

# Change to:
from anthropic import Anthropic, MessageStream
```

**However**, the Agent SDK is a **separate tool** that's part of Claude Code, not a Python package. It's accessed via CLI, not Python imports.

#### Option 2: Use MCP (Model Context Protocol)

The Agent SDK functionality might be available through MCP:

```bash
manus-mcp-cli --help
```

#### Option 3: Revert to Direct Anthropic API

Use the standard Anthropic Python SDK with custom agent loop:

```python
from anthropic import Anthropic

client = Anthropic()
# Implement custom agent loop
```

### Recommended Fix

**The refactor has a fundamental architectural issue.** The "Agent SDK" referenced in the documentation appears to be:

1. **Claude Code's built-in agent system** (not a Python package)
2. **Not directly importable** in Python code
3. **Requires different implementation approach**

**We need to:**

1. Clarify what "Agent SDK" means
2. Determine if it's the Anthropic Python SDK
3. Reimplement using available tools (Anthropic SDK or MCP)
4. Or use Claude Code's agent capabilities differently

---

## 🚨 Critical Issue #2: Incorrect Architecture Assumption

### Problem

The refactor assumes `claude-agent-sdk` provides:
- `query()` function for agent execution
- `ClaudeAgentOptions` for configuration
- Built-in tools (Bash, Read, Write, etc.)

**These may not exist as a Python package.**

### Impact

- ❌ Core architecture is based on non-existent package
- ❌ All 14 agent files need reimplementation
- ❌ Examples and apps won't work

### Resolution

Need to determine the correct implementation approach:

1. **If using Anthropic Python SDK:**
   ```python
   from anthropic import Anthropic
   
   client = Anthropic()
   response = client.messages.create(
       model="claude-3-5-sonnet-20241022",
       messages=[{"role": "user", "content": prompt}]
   )
   ```

2. **If using Claude Code Agent features:**
   - May need to use MCP
   - May need to use subprocess calls
   - May need different architecture

3. **If using custom agent framework:**
   - Implement agent loop manually
   - Use Anthropic SDK for LLM calls
   - Implement tools ourselves

---

## 🔍 Investigation Needed

### Questions to Answer

1. **What is "claude-agent-sdk"?**
   - Is it a real Python package?
   - Is it part of Claude Code?
   - Is it the Anthropic Python SDK?

2. **Where is the Agent SDK documentation from?**
   - The migration references Agent SDK docs
   - Need to verify these are real/current

3. **What tools are actually available?**
   - Bash, Read, Write, etc.
   - Are these MCP tools?
   - Are these Claude Code features?

### Investigation Steps

```bash
# Check if it's an MCP tool
manus-mcp-cli list-tools

# Check Anthropic SDK
pip3 install anthropic
python3 -c "import anthropic; print(dir(anthropic))"

# Check for agent-related functionality
python3 -c "import anthropic; help(anthropic)"
```

---

## 🛠️ Immediate Actions Required

### Before This Can Be Deployed

1. **Clarify Package Name**
   - [ ] Verify correct package name
   - [ ] Check if publicly available
   - [ ] Get installation instructions

2. **Test Import**
   - [ ] Install correct package
   - [ ] Verify import works
   - [ ] Test basic functionality

3. **Update Code if Needed**
   - [ ] Fix imports if package name wrong
   - [ ] Reimplement if package doesn't exist
   - [ ] Update all 14 agent files

4. **Update Documentation**
   - [ ] Correct installation instructions
   - [ ] Update examples
   - [ ] Fix migration guide

### Alternative: Pivot to Anthropic SDK

If `claude-agent-sdk` doesn't exist as a package, we need to:

1. **Reimplement using Anthropic Python SDK**
   ```python
   from anthropic import Anthropic
   
   class BaseAgentSDK:
       def __init__(self):
           self.client = Anthropic()
       
       async def _execute_query(self, prompt):
           # Implement agent loop with Anthropic SDK
           # Use tool use / function calling
           pass
   ```

2. **Implement Tools Ourselves**
   - Bash execution (subprocess)
   - File operations (pathlib)
   - Web search (requests + search API)

3. **Update All Agents**
   - Rewrite to use new implementation
   - Test thoroughly

---

## 📊 Impact Assessment

### If Package Doesn't Exist

| Component | Status | Effort to Fix |
|-----------|--------|---------------|
| Base Agent | ❌ Broken | 2-3 days |
| Standard Agents (5) | ❌ Broken | 1 week |
| ML/DS Agents (2) | ❌ Broken | 2-3 days |
| Multi-Agents (1) | ❌ Broken | 1-2 days |
| Examples | ❌ Broken | 1 day |
| Apps | ❌ Broken | 1 day |
| **Total** | **❌ Complete Rewrite** | **2-3 weeks** |

### If Package Exists But Different

| Component | Status | Effort to Fix |
|-----------|--------|---------------|
| Base Agent | ⚠️ Needs Updates | 1-2 days |
| All Agents | ⚠️ Needs Updates | 2-3 days |
| Examples | ⚠️ Needs Updates | 1 day |
| Apps | ⚠️ Needs Updates | 1 day |
| **Total** | **⚠️ Moderate Fixes** | **1 week** |

---

## 🎯 Recommendation

### STOP DEPLOYMENT

**Do not merge or deploy** until we:

1. ✅ Verify `claude-agent-sdk` package exists and is accessible
2. ✅ Test imports work correctly
3. ✅ Run at least one agent successfully
4. ✅ Update documentation with correct instructions

### Next Steps

1. **Immediate (Today)**
   - Investigate claude-agent-sdk package
   - Check Anthropic SDK documentation
   - Test if MCP provides agent capabilities
   - Determine correct implementation approach

2. **If Package Exists (1-2 days)**
   - Install and test
   - Fix any import issues
   - Update documentation
   - Run validation tests

3. **If Package Doesn't Exist (2-3 weeks)**
   - Reimplement using Anthropic SDK
   - Build custom agent loop
   - Implement tools ourselves
   - Retest everything

---

## 📞 Questions for Stakeholders

1. **Where did the Agent SDK documentation come from?**
   - Was it from official Anthropic docs?
   - Was it from Claude Code documentation?
   - Was it from a third-party source?

2. **Have you used claude-agent-sdk before?**
   - In what context?
   - How was it installed?
   - What version?

3. **What is the goal?**
   - Use Anthropic's official tools?
   - Use Claude Code's agent features?
   - Build custom agent framework?

---

## ⚠️ Code Review Status Update

**Original Assessment:** B+ (Very Good)  
**Updated Assessment:** **INCOMPLETE** ❌

**Reason:** Core dependency issue makes code non-functional

**Revised Recommendation:** **DO NOT MERGE** until dependency issue resolved

---

*Critical Issues Document - December 17, 2025*
