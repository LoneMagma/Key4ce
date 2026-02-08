# Terminal Typing Game - Minimalist Design Doc

> **Philosophy: Clean. Minimal. Quirky. Powerful.**

---

## 🎨 UI Design Philosophy

### Core Principles
- **ONE thing at a time** - No overwhelming screens
- **Smooth animations** - Everything flows, nothing jumps
- **Breathing room** - Generous spacing, not cramped
- **Instant feedback** - You always know what's happening
- **Hidden depth** - Simple surface, powerful underneath

---

## 🖥️ UI Mockups & Animations

### Main Menu (Animated)

```
     ┌─────────────────────────────────────┐
     │                                     │
     │        ╔╦╗╔═╗╦═╗╔╦╗╦╔╗╔╔═╗╦        │
     │        ║ ║╣ ╠╦╝║║║║║║║╠═╣║        │
     │        ╩ ╚═╝╩╚═╩ ╩╩╝╚╝╩ ╩╩═╝      │
     │         ╦  ╦╔═╗╦  ╔═╗╔═╗╦╔╦╗╦ ╦   │
     │         ╚╗╔╝║╣ ║  ║ ║║  ║ ║ ╚╦╝   │
     │          ╚╝ ╚═╝╩═╝╚═╝╚═╝╩ ╩  ╩    │
     │                                     │
     │            > Quick Start            │
     │              Practice               │
     │              Challenge              │
     │              Stats                  │
     │                                     │
     │         [ESC] quit  [?] help        │
     └─────────────────────────────────────┘

Animation: Title subtly pulses with RGB color shift
          Cursor smoothly moves between options
          Selected option has animated underline: ════
```

### Typing Screen (Clean & Minimal)

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  The quick brown fox jumps over the lazy dog near            │
│  the riverbank where children often play during              │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓          │
│                                                               │
│                                                               │
│                    72 wpm · 98% · 0:45                        │
│                    ▓▓▓▓▓▓▓▓▓▓▓░░░░ 67%                        │
│                                                               │
└───────────────────────────────────────────────────────────────┘

Features:
- Already typed text fades to dim gray
- Current word is bold/highlighted
- Upcoming text is slightly dimmed
- Cursor is a smooth blinking block █
- Progress bar fills with smooth animation
- Wrong characters show in red, then shake slightly
- Stats update smoothly, numbers count up/down
```

### Loading Animations (The Cool Stuff!)

**Pipe Flow Animation** (while loading content)
```
╔═══════════════════════════════════════╗
║                                       ║
║    Loading content...                 ║
║                                       ║
║    ┌─────────────────────────────┐    ║
║    │ ████░░░░░░░░░░░░░░░░░░░░░░ │    ║
║    └─────────────────────────────┘    ║
║                                       ║
╚═══════════════════════════════════════╝

Animation: Block moves left to right smoothly
          Different styles: ▓▒░, ◢◣◤◥, ▀▄, ┃━, ●◐◑◒
```

**Matrix-Style Text Rain** (transition between modes)
```
   ╔╦╗╔═╗╦═╗╔╦╗╦╔╗╔╔═╗╦  
   ║ ║╣ ╠╦╝║║║║║║║╠═╣║  
   ╩ ╚═╝╩╚═╩ ╩╩╝╚╝╩ ╩╩═╝
   
   [Vertical text streams falling]
   Characters cascade down the screen
   Then resolve into the game mode title
```

**Typewriter Effect** (for hints/tips)
```
Tip: Focus on accuracy first, speed will follow...
     [Text appears character by character]
     [With authentic typewriter sound (optional)]
```

**Wave Progress Bar**
```
Progress: [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░] 73%
          [Bar has wave/pulse animation]
          [Colors shift: green → yellow → red based on performance]
```

### Mode Selection Screen

```
┌──────────────────────────────────────────────┐
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  QUICK   │  │ PRACTICE │  │ CHALLENGE│  │
│  │  START   │  │          │  │          │  │
│  │          │  │  Random  │  │  Daily   │  │
│  │  Jump    │  │  text    │  │  test    │  │
│  │  right   │  │  session │  │  ranked  │  │
│  │  in      │  │          │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│       ▲                                      │
│   [selected]                                 │
└──────────────────────────────────────────────┘

Animation: Cards slide in from edges
          Selected card lifts up slightly (using spacing)
          Border glows on selection
```

---

## ✨ Concrete Features to Add

### 1. **Dynamic Text Preview**
Before starting, show a blurred preview that clears as you type
```
The quick brown fox...
[blurred upcoming text]

→ As you type, text ahead unblurs gradually
→ Creates a "revealing" effect
```

### 2. **Combo Meter**
Like fighting games - builds as you type correctly
```
COMBO: x23 🔥🔥🔥
[Meter fills, adds flame icons at milestones]
Break combo = meter resets with "crunch" visual
Combo affects final score multiplier
```

### 3. **Ghost Racer**
Race against your previous best performance
```
Your text: The quick brown fox█
Ghost:     The quick brown fox jumps
           ↑ (shows where your best attempt was at this time)

Visual: Ghost cursor moves ahead/behind you
       Transparent/dimmed to not distract
```

### 4. **Live WPM Graph**
Minimal live graph showing WPM over time
```
WPM
90│        ╱╲
  │       ╱  ╲    ╱
60│   ╱╲╱    ╲  ╱
  │  ╱        ╲╱
30│╱
  └────────────────→ time
  
Updates in real-time as you type
Shows fluctuations, helps maintain consistency
```

### 5. **Keyboard Heat Map** (Live)
Shows which keys you're hitting
```
  Q W E R T Y U I O P
   A S D F G H J K L
    Z X C V B N M

Animation: Keys light up briefly when pressed
          Brighter = more frequent
          Fades over time
          Creates beautiful visual patterns
```

### 6. **Zen Mode**
Ultra-minimal: just you and the text
```
┌─────────────────────────────────────┐
│                                     │
│                                     │
│         your text here█             │
│                                     │
│                                     │
│                                     │
└─────────────────────────────────────┘

No stats, no timer, no pressure
Just typing
Stats shown only at the end
```

### 7. **Power-Ups** (Gamification)
Unlock during gameplay based on performance
```
✨ FOCUS MODE: Screen dims everything but current word
⚡ TIME WARP: Slow-mo effect, easier to type fast
🎯 PRECISION: Show exact finger position hints
🔥 STREAK SAVER: One mistake doesn't break combo
🌈 RAINBOW MODE: Typed text becomes rainbow colored
```

### 8. **Text Sources - Smart & Varied**

**Code Snippets:**
- Real GitHub trending repos
- Your own git history (if authorized)
- Language-specific challenges
- Bug fixing mode (type to fix intentional bugs)

**Prose:**
- Classic literature (Project Gutenberg)
- Tech articles (HackerNews, dev.to)
- Movie scripts
- Song lyrics (with beat indicators)
- Reddit top posts

**Dynamic Content:**
- News headlines (live)
- Wikipedia "On This Day"
- Random facts
- Programming documentation
- Custom user playlists

### 9. **Session Rewind**
After completing, watch a replay of your session
```
[▶] Replay    [⏩] 2x speed    [⏸] Pause

Shows exactly when you made mistakes
Where you slowed down
Where you sped up
Can skip to interesting moments
```

### 10. **Achievements with Visual Flair**
```
╔═══════════════════════════════════╗
║   🏆 ACHIEVEMENT UNLOCKED 🏆      ║
║                                   ║
║        "SPEED DEMON"              ║
║     Reached 100 WPM!              ║
║                                   ║
║   [Fireworks animation plays]     ║
╚═══════════════════════════════════╝

Achievement notification slides in from top
Celebrates with ASCII fireworks/confetti
Then slides out smoothly
```

---

## 📊 POST-SESSION ANALYSIS REPORT

### The Killer Feature: Comprehensive Report

```
╔═══════════════════════════════════════════════════════════════╗
║                    SESSION COMPLETE                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              PERFORMANCE SUMMARY                    │     ║
║  ├─────────────────────────────────────────────────────┤     ║
║  │                                                     │     ║
║  │  Final WPM:       78.4  ████████░░ [+12 from avg]  │     ║
║  │  Accuracy:        96.2% █████████░ [Excellent]     │     ║
║  │  Consistency:     8.7/10 ████████░░               │     ║
║  │  Time:            2m 34s                           │     ║
║  │  Words Typed:     312                              │     ║
║  │                                                     │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              WPM OVER TIME                          │     ║
║  │                                                     │     ║
║  │  90│    ╱╲     ╱╲                                  │     ║
║  │    │   ╱  ╲   ╱  ╲    ╱╲                          │     ║
║  │  75│  ╱    ╲ ╱    ╲  ╱  ╲                         │     ║
║  │    │ ╱      ╲      ╲╱    ╲                        │     ║
║  │  60│╱                      ╲                       │     ║
║  │    └────────────────────────────→                  │     ║
║  │    0s        60s       120s                        │     ║
║  │                                                     │     ║
║  │  🔍 You started strong, dipped at 80s (fatigue?)   │     ║
║  │     Recovered well in final stretch!               │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              ERROR ANALYSIS                         │     ║
║  │                                                     │     ║
║  │  Total Errors: 12                                  │     ║
║  │                                                     │     ║
║  │  Most Common Mistakes:                             │     ║
║  │    • 'teh' → 'the' (5 times) ⚠️                    │     ║
║  │    • 'adn' → 'and' (3 times)                       │     ║
║  │    • Extra spaces   (2 times)                      │     ║
║  │    • 'taht' → 'that' (2 times)                     │     ║
║  │                                                     │     ║
║  │  🎯 Practice words: the, and, that                 │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              KEYBOARD HEATMAP                       │     ║
║  │                                                     │     ║
║  │    Q W E R T Y U I O P                             │     ║
║  │    ░ ░ █ ▓ ▓ ░ ░ ▓ ░ ░    [E, R, T, I most used] │     ║
║  │     A S D F G H J K L                              │     ║
║  │     ▓ ▓ ░ ░ ░ ▓ ░ ░ ░                             │     ║
║  │      Z X C V B N M                                 │     ║
║  │      ░ ░ ░ ░ ░ ▓ ░                                │     ║
║  │                                                     │     ║
║  │  ▓▓▓ High usage  ░░░ Low usage                     │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              TYPING RHYTHM                          │     ║
║  │                                                     │     ║
║  │  Key Interval (ms): 145 avg                        │     ║
║  │  ██████████████████░░░░░░ Consistent               │     ║
║  │                                                     │     ║
║  │  💡 Your rhythm is improving! Was 162ms last week  │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              PROBLEM PAIRS                          │     ║
║  │                                                     │     ║
║  │  Digraphs you struggle with:                       │     ║
║  │    'th' - 12% slower than average                  │     ║
║  │    'ng' - 18% slower than average                  │     ║
║  │    'qu' - 9% slower than average                   │     ║
║  │                                                     │     ║
║  │  🎯 Custom practice generated for you!             │     ║
║  │     Run: practice --focus digraphs                 │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              ACHIEVEMENTS                           │     ║
║  │                                                     │     ║
║  │  ✨ ACCURACY ACE    - 95%+ accuracy (1/10)         │     ║
║  │  🔥 SPEED DEMON     - 75+ WPM       (1/100)        │     ║
║  │  📈 IMPROVEMENT     - +10 WPM gain  (NEW!)         │     ║
║  │                                                     │     ║
║  │  Next goal: CENTURION (100 WPM)    ▓▓▓▓▓▓▓░░░ 78%  │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              COMPARISON                             │     ║
║  │                                                     │     ║
║  │  Your Best:        82.1 WPM on Dec 15              │     ║
║  │  Today's Avg:      76.3 WPM                         │     ║
║  │  This Week:        74.8 WPM avg                     │     ║
║  │  Last Week:        66.2 WPM avg  [+13% improvement]│     ║
║  │                                                     │     ║
║  │  Global Rank:      Top 23% (of 15,234 users)       │     ║
║  │  Percentile:       77th                             │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              AI INSIGHTS                            │     ║
║  │                                                     │     ║
║  │  💬 "Your speed is great, but you're sacrificing   │     ║
║  │      accuracy. Try slowing down by 5 WPM - your    │     ║
║  │      overall score will likely improve!"           │     ║
║  │                                                     │     ║
║  │  💬 "You typed 'the' incorrectly 5 times. This is  │     ║
║  │      a common pattern. Would you like targeted     │     ║
║  │      practice?"                                    │     ║
║  │                                                     │     ║
║  │  💬 "Excellent consistency! Your WPM variance was  │     ║
║  │      only 8.3 - that's better than 85% of users."  │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              RECOMMENDATIONS                        │     ║
║  │                                                     │     ║
║  │  Based on this session:                            │     ║
║  │                                                     │     ║
║  │  1. Practice common word combos (the, and, that)   │     ║
║  │  2. Focus on 'th' and 'ng' digraphs                │     ║
║  │  3. Try Zen mode to improve consistency            │     ║
║  │  4. Take breaks every 90 seconds (you dipped)      │     ║
║  │                                                     │     ║
║  │  🎯 Next Challenge: Beat your 82 WPM record!       │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │              SHARE YOUR SCORE                       │     ║
║  │                                                     │     ║
║  │  [Export as PNG] [Copy to Clipboard] [Tweet]       │     ║
║  │                                                     │     ║
║  │  TerminalVelocity │ 78 WPM │ 96% acc │ +12 ↑       │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  [S] Save Report  [R] Retry  [M] Menu  [Q] Quit              ║
╚═══════════════════════════════════════════════════════════════╝
```

### Report Export Options

**1. Terminal View** (shown above)
Full-featured, interactive report in terminal

**2. PNG Export**
```
╔═══════════════════════════╗
║  My Typing Session        ║
║  78 WPM · 96% · 2m 34s   ║
║  [Mini graph visual]      ║
║  +12 WPM improvement!     ║
╚═══════════════════════════╝
→ Shareable image for social media
```

**3. JSON Export**
```json
{
  "session_id": "abc123",
  "wpm": 78.4,
  "accuracy": 96.2,
  "errors": [...],
  "timeline": [...],
  "heatmap": {...}
}
→ For data analysis, external tools
```

**4. Markdown Report**
```markdown
# Typing Session - Feb 8, 2026

**WPM:** 78.4 (+12 from average)
**Accuracy:** 96.2%

## Analysis
- Strong start, fatigue at 80s
- Common errors: 'the', 'and'
...

→ Great for keeping in notes/journal
```

---

## 🎯 Feature Priority

### Phase 1 (Core - Week 1-2)
1. ✅ Basic typing engine
2. ✅ Minimal UI with smooth cursor
3. ✅ Real-time WPM/accuracy
4. ✅ Simple progress bar animation
5. ✅ Basic post-session stats

### Phase 2 (Polish - Week 3-4)
1. ✅ Full session report (comprehensive)
2. ✅ Multiple text sources
3. ✅ Ghost racer
4. ✅ Combo meter
5. ✅ Loading animations (pipe flow, etc.)
6. ✅ Keyboard heatmap

### Phase 3 (Advanced - Week 5-6)
1. ✅ Error pattern analysis
2. ✅ AI insights/recommendations
3. ✅ Achievement system
4. ✅ Theme system
5. ✅ Session replay
6. ✅ Export functionality

### Phase 4 (Extra - Week 7+)
1. ✅ Zen mode
2. ✅ Power-ups
3. ✅ Custom practice generator
4. ✅ Live WPM graph
5. ✅ Sound effects (optional)

---

## 🏗️ Technical Implementation Notes

### Animation System
```python
# Smooth animation using frame interpolation
class Animation:
    def __init__(self, start, end, duration_ms):
        self.start = start
        self.end = end
        self.duration = duration_ms
        self.start_time = time.time()
    
    def get_current_value(self):
        elapsed = (time.time() - self.start_time) * 1000
        progress = min(elapsed / self.duration, 1.0)
        # Easing function for smooth motion
        eased = self.ease_in_out_cubic(progress)
        return self.start + (self.end - self.start) * eased
    
    def ease_in_out_cubic(self, t):
        return 4*t*t*t if t < 0.5 else 1-pow(-2*t+2, 3)/2
```

### Error Tracking
```python
class ErrorTracker:
    def __init__(self):
        self.errors = []
        self.digraph_speeds = {}
        self.common_mistakes = defaultdict(int)
    
    def log_error(self, expected, typed, position, timestamp):
        self.errors.append({
            'expected': expected,
            'typed': typed,
            'position': position,
            'timestamp': timestamp
        })
        
        # Track common mistakes
        if len(typed) == len(expected):
            self.common_mistakes[f"{typed}→{expected}"] += 1
```

### Session Replay
```python
class SessionRecorder:
    def __init__(self):
        self.keystrokes = []
        self.start_time = None
    
    def record_keystroke(self, char, timestamp, is_correct):
        self.keystrokes.append({
            'char': char,
            'time': timestamp - self.start_time,
            'correct': is_correct,
            'wpm_at_time': self.calculate_wpm()
        })
    
    def replay(self, speed=1.0):
        # Play back the session at adjustable speed
        for keystroke in self.keystrokes:
            time.sleep(keystroke['time'] / speed)
            # Render the keystroke
```

---

## 🎨 Theme Examples

### Minimal themes (choose color palettes only)

**Cyberpunk**
```
Background: #0a0e27
Primary:    #00ff9f
Secondary:  #ff006a
Accent:     #00d4ff
Text:       #e0e0e0
```

**Nord**
```
Background: #2e3440
Primary:    #88c0d0
Secondary:  #81a1c1
Accent:     #a3be8c
Text:       #eceff4
```

**Dracula**
```
Background: #282a36
Primary:    #bd93f9
Secondary:  #ff79c6
Accent:     #50fa7b
Text:       #f8f8f2
```

**Monokai**
```
Background: #272822
Primary:    #66d9ef
Secondary:  #a6e22e
Accent:     #f92672
Text:       #f8f8f2
```

---

## 🚀 Quick Start Implementation

### Minimal Tech Stack (Recommended)
```
Python 3.10+
├── rich (TUI framework - beautiful, simple)
├── textual (if you want even more polish)
├── sqlite3 (built-in, for data)
└── requests (for fetching content)

Alternative:
Rust + ratatui (if you want performance)
```

### File Structure (Simplified)
```
terminalvelocity/
├── main.py              # Entry point
├── ui/
│   ├── screens.py       # All screens
│   ├── animations.py    # Animation helpers
│   └── components.py    # Reusable UI parts
├── game/
│   ├── engine.py        # Core typing logic
│   ├── analyzer.py      # Session analysis
│   └── recorder.py      # Session recording
├── content/
│   └── loader.py        # Load text from sources
├── data/
│   └── database.py      # SQLite operations
└── themes/
    └── themes.json      # Color schemes
```

---

## ✅ Final Checklist

**Must-Haves:**
- [ ] Smooth animations (cursor, progress, transitions)
- [ ] Clean minimal UI (one thing at a time)
- [ ] Comprehensive post-session report
- [ ] Error pattern analysis
- [ ] Ghost racer (race your best)
- [ ] Combo meter
- [ ] Keyboard heatmap
- [ ] Multiple text sources
- [ ] Export functionality

**Nice-to-Haves:**
- [ ] Zen mode
- [ ] Power-ups
- [ ] Session replay
- [ ] Live WPM graph
- [ ] Achievements
- [ ] Sound effects

**Future:**
- [ ] Multiplayer
- [ ] Online leaderboards
- [ ] Community challenges

---

## 🎯 The Goal

Create a typing game that:
1. **Feels amazing** - Every interaction is smooth and satisfying
2. **Looks minimal** - Clean, breathing room, no clutter
3. **Is quirky** - Unique animations, personality, fun
4. **Makes you better** - Actionable insights, not just stats
5. **Keeps you coming back** - Progress tracking, achievements, improvement visible

---

*Let's build something beautiful.*
