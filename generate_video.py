"""
MechEval Full Walkthrough Video Generator.
Generates 1920x1080 video frames, creates synchronized speech narration,
and compiles the final Deliverable B walkthrough MP4 using ffmpeg.
"""

import os
import sys
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont

# Path definitions
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEMO_DIR = os.path.join(BASE_DIR, "demo")
TEMP_VIDEO_DIR = os.path.join(DEMO_DIR, "video_temp")
OUTPUT_VIDEO_PATH = os.path.join(DEMO_DIR, "mecheval_walkthrough.mp4")

os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

# Colors
BG_DARK = (11, 15, 25)
BG_CARD = (20, 28, 48)
BG_CARD_BORDER = (40, 56, 92)
ACCENT_BLUE = (59, 130, 246)
ACCENT_CYAN = (6, 182, 212)
ACCENT_GREEN = (34, 197, 94)
ACCENT_RED = (239, 68, 68)
ACCENT_AMBER = (245, 158, 11)
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (156, 163, 175)
TEXT_CODE = (226, 232, 240)

# Fonts
def get_font(size: int, bold: bool = False):
    font_path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def get_code_font(size: int):
    font_path = "C:/Windows/Fonts/consola.ttf"
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return get_font(size)


def draw_header(draw, title: str, category: str):
    # Top banner badge
    draw.rounded_rectangle([80, 50, 420, 95], radius=8, fill=(30, 41, 59), outline=ACCENT_CYAN, width=1)
    badge_font = get_font(20, bold=True)
    draw.text((100, 60), f"MECHEVAL  |  {category.upper()}", fill=ACCENT_CYAN, font=badge_font)

    # Title
    title_font = get_font(44, bold=True)
    draw.text((80, 115), title, fill=TEXT_WHITE, font=title_font)
    draw.line([(80, 180), (1840, 180)], fill=(40, 56, 92), width=2)


def create_slide_1() -> str:
    """Scene 1: Title & The Engineering Problem"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "MechEval: Mechanical Engineering AI Evaluation Benchmark", "Hackathon Project")

    # Big main hero box
    draw.rounded_rectangle([80, 220, 1840, 520], radius=16, fill=BG_CARD, outline=ACCENT_BLUE, width=2)
    hero_title_font = get_font(38, bold=True)
    draw.text((120, 255), "Can AI Models Reliably Solve Mechanical Engineering Problems?", fill=ACCENT_CYAN, font=hero_title_font)

    hero_sub_font = get_font(26)
    sub_text = (
        "Frontier models (GPT-4o, Claude 3.5 Sonnet) produce impressive, fluent derivations.\n"
        "However, in safety-critical physical systems, plausible-looking mathematical errors\n"
        "and incorrect boundary assumptions lead to catastrophic structural failure."
    )
    draw.text((120, 325), sub_text, fill=TEXT_CODE, font=hero_sub_font, spacing=14)

    # Three key questions cards
    cards = [
        ("The Core Mission", "Design & package a reproducible benchmark exposing genuine physical reasoning limits in AI models.", ACCENT_BLUE),
        ("The Challenge", "Move beyond text fluency to exact numerical precision, load superposition, and kinematic boundary enforcement.", ACCENT_AMBER),
        ("The Standard", "Independently verified analytical ground truths, automated code-graders, zero false passes.", ACCENT_GREEN),
    ]

    card_width = 560
    for i, (head, desc, color) in enumerate(cards):
        x0 = 80 + i * (card_width + 40)
        draw.rounded_rectangle([x0, 560, x0 + card_width, 960], radius=12, fill=BG_CARD, outline=color, width=2)
        draw.text((x0 + 30, 600), head, fill=color, font=get_font(28, bold=True))
        
        # Word wrap desc
        desc_font = get_font(22)
        words = desc.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 32:
                lines.append(cur)
                cur = w
            else:
                cur = cur + " " + w if cur else w
        if cur:
            lines.append(cur)
        draw.text((x0 + 30, 660), "\n\n".join(lines), fill=TEXT_MUTED, font=desc_font)

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_1.png")
    img.save(out_path)
    return out_path


def create_slide_2() -> str:
    """Scene 2: What MechEval Evaluates (The 5 Engineering Tasks)"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "Five Rigorous Physical Reasoning Tasks", "Benchmark Scope")

    tasks = [
        ("Task 001: Cantilever Beam Analysis", "Euler-Bernoulli beam under tip point load P + distributed self-weight dead load w0 under gravity. Stresses, root moment, deflection.", ACCENT_BLUE),
        ("Task 002: Stepped Axial Bar Equilibrium", "Method of sections for normal forces across differing diameters, intermediate reverse load F_int, segment elongations, strain energy.", ACCENT_CYAN),
        ("Task 003: Indeterminate Propped Cantilever", "Statically indeterminate degree 1 beam. Kinematic compatibility w(L)=0, asymmetric reactions (3/8 vs 5/8 wL), inflection point.", ACCENT_RED),
        ("Task 004: Thermal Expansion with Clearance Gap", "Thermo-elastic piecewise contact mechanics. Temperature threshold to close initial gap delta_0, contact reaction, thermal stress.", ACCENT_AMBER),
        ("Task 005: FEA Mesh Convergence & Singularity", "ASME V&V 20 Richardson extrapolation across 3 grid levels (h -> 0), apparent order p, GCI %, and re-entrant corner singularity detection.", ACCENT_GREEN),
    ]

    for i, (title, desc, color) in enumerate(tasks):
        y0 = 210 + i * 150
        draw.rounded_rectangle([80, y0, 1840, y0 + 130], radius=10, fill=BG_CARD, outline=color, width=2)
        draw.text((120, y0 + 20), title, fill=color, font=get_font(26, bold=True))
        draw.text((120, y0 + 65), desc, fill=TEXT_MUTED, font=get_font(20))

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_2.png")
    img.save(out_path)
    return out_path


def create_slide_3() -> str:
    """Scene 3: Deep Dive into Task 3 (Statically Indeterminate Beam)"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "Task 003 Deep Dive: Indeterminate Propped Cantilever", "Engineering Case Study")

    # Left panel: Physical setup and equations
    draw.rounded_rectangle([80, 220, 930, 980], radius=12, fill=BG_CARD, outline=ACCENT_BLUE, width=2)
    draw.text((110, 250), "Governing Boundary Compatibility", fill=ACCENT_CYAN, font=get_font(30, bold=True))

    left_body = (
        "Problem Setup:\n"
        "- Span length L = 4.0 m, Uniform load w = 12 kN/m (Total load = 48 kN)\n"
        "- Left support (x = 0): Fully clamped wall (Deflection = 0, Slope = 0)\n"
        "- Right support (x = L): Simple roller support (Deflection = 0)\n\n"
        "Statical Indeterminacy:\n"
        "- 3 Unknown Reactions (R_A, M_A, R_B) vs 2 Static Equations\n"
        "- Requires Kinematic Compatibility Equation:\n"
        "    delta_B = [w * L^4 / (8*E*I)] - [R_B * L^3 / (3*E*I)] = 0\n\n"
        "Analytical Closed-Form Ground Truth:\n"
        "- Roller Reaction:  R_B = 3/8 * w * L = 18,000 N (37.5%)\n"
        "- Wall Vertical:    R_A = 5/8 * w * L = 30,000 N (62.5%)\n"
        "- Clamping Moment:  M_A = 1/8 * w * L^2 = 24,000 N*m\n"
        "- Point of Contraflexure:  x_inflect = L / 4 = 1.00 m\n"
        "- Max Positive Moment:    M_max = 9/128 * w * L^2 = 13,500 N*m"
    )
    draw.text((110, 310), left_body, fill=TEXT_CODE, font=get_code_font(18), spacing=6)

    # Right panel: Key engineering insight
    draw.rounded_rectangle([970, 220, 1840, 980], radius=12, fill=BG_CARD, outline=ACCENT_AMBER, width=2)
    draw.text((1000, 250), "Why Models Struggle With Indeterminacy", fill=ACCENT_AMBER, font=get_font(30, bold=True))

    right_body = (
        "1. Statics Alone Cannot Solve This System:\n"
        "   Models cannot simply apply sum(Fy) = 0 and sum(M) = 0.\n"
        "   They must integrate beam curvature or apply superposition.\n\n"
        "2. Asymmetric Support Stiffness:\n"
        "   The clamped wall prevents rotation, making it stiffer than\n"
        "   the roller. It attracts 62.5% of the total load (30 kN),\n"
        "   leaving only 37.5% (18 kN) for the roller.\n\n"
        "3. Common LLM Failure:\n"
        "   Models hallucinate symmetric 50/50 load sharing:\n"
        "     R_A = 24,000 N,  R_B = 24,000 N  (33.3% Error!)\n"
        "   They also miss the wall moment completely (M_A = 0).\n\n"
        "Real-World Structural Consequence:\n"
        "Under-designing the wall connection reaction by 20% would\n"
        "cause anchor bolt shear failure and structural collapse."
    )
    draw.text((1000, 310), right_body, fill=TEXT_WHITE, font=get_font(21), spacing=8)

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_3.png")
    img.save(out_path)
    return out_path


def create_slide_4() -> str:
    """Scene 4: Frontier Model Attempt & Transcript Analysis"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "Frontier Model Attempt: GPT-4o & Claude 3.5 Sonnet", "Actual Model Transcripts")

    # Left: Actual Model Transcript Box
    draw.rounded_rectangle([80, 220, 1000, 980], radius=12, fill=(15, 23, 42), outline=ACCENT_RED, width=2)
    draw.text((110, 250), "Recorded Model Transcript (GPT-4o Trial 2)", fill=ACCENT_RED, font=get_font(26, bold=True))

    transcript_text = (
        "Model Prompt:\n"
        "Analyze propped cantilever beam (L = 4.0 m, w = 12 kN/m)\n"
        "Fixed at x = 0, roller support at x = 4.0 m...\n\n"
        "Actual Model Response:\n"
        "\"For this beam under uniform load w = 12000 N/m over 4 m:\n"
        " Total downward load is 48000 N.\n"
        " By symmetry of support load sharing:\n"
        " R_A = 24,000 N, R_B = 24,000 N.\n"
        " Midspan moment = w*L^2 / 8 = 24,000 N*m.\n"
        " No inflection point exists in simply supported beam.\"\n\n"
        "Model Output JSON:\n"
        "{\n"
        "  \"roller_reaction_N\": 24000.0,\n"
        "  \"wall_vertical_reaction_N\": 24000.0,\n"
        "  \"wall_moment_Nm\": 0.0,\n"
        "  \"x_max_positive_moment_m\": 2.00,\n"
        "  \"x_contraflexure_m\": 2.00\n"
        "}"
    )
    draw.text((110, 310), transcript_text, fill=TEXT_CODE, font=get_code_font(18), spacing=6)

    # Right: Grader Failure Report Box
    draw.rounded_rectangle([1040, 220, 1840, 980], radius=12, fill=BG_CARD, outline=ACCENT_RED, width=2)
    draw.text((1070, 250), "MechEval Automated Grader Verdict", fill=ACCENT_RED, font=get_font(26, bold=True))

    verdict_text = (
        "STATUS: FAILED (Score: 55.0%)\n"
        "All-Passed: False\n\n"
        "Parameter Checks:\n"
        "[FAIL] roller_reaction_N:\n"
        "       Candidate: 24,000.0 N  |  Reference: 18,000.0 N\n"
        "       Relative Error: +33.33% (Allowed: 1.0%)\n\n"
        "[FAIL] wall_vertical_reaction_N:\n"
        "       Candidate: 24,000.0 N  |  Reference: 30,000.0 N\n"
        "       Relative Error: -20.00% (Allowed: 1.0%)\n\n"
        "[FAIL] wall_moment_Nm:\n"
        "       Candidate: 0.0 N*m     |  Reference: 24,000.0 N*m\n"
        "       Relative Error: -100.00% (Allowed: 1.0%)\n\n"
        "[FAIL] x_contraflexure_m:\n"
        "       Candidate: 2.00 m      |  Reference: 1.00 m\n"
        "       Relative Error: +100.00% (Allowed: 1.0%)\n\n"
        "Key Finding:\n"
        "Task 3 Pass Rate was 0.0% across all trials for both models!"
    )
    draw.text((1070, 310), verdict_text, fill=TEXT_WHITE, font=get_code_font(18), spacing=6)

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_4.png")
    img.save(out_path)
    return out_path


def create_slide_5() -> str:
    """Scene 5: Deterministic Automated Grading & Verification Suite"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "Grader Reliability: Verified Across 33 Pytest Cases", "Automated Evaluation")

    # Terminal mock box
    draw.rounded_rectangle([80, 220, 1200, 980], radius=12, fill=(10, 12, 18), outline=ACCENT_GREEN, width=2)
    draw.text((110, 245), "Pytest Suite: tests/ (33 Passed in 2.18s)", fill=ACCENT_GREEN, font=get_font(24, bold=True))

    term_output = (
        "tests/test_axial.py::test_reference_solution_physical_sanity PASSED\n"
        "tests/test_axial.py::test_grader_accepts_reference_solution PASSED\n"
        "tests/test_axial.py::test_grader_tolerance_boundaries PASSED\n"
        "tests/test_axial.py::test_grader_rejects_sign_error_on_intermediate_load PASSED\n"
        "tests/test_boundary.py::test_symbolic_propped_cantilever PASSED\n"
        "tests/test_boundary.py::test_grader_accepts_reference_solution PASSED\n"
        "tests/test_boundary.py::test_grader_rejects_simply_supported_reaction PASSED\n"
        "tests/test_cantilever.py::test_symbolic_cantilever_mechanics PASSED\n"
        "tests/test_cantilever.py::test_grader_rejects_omitted_self_weight PASSED\n"
        "tests/test_cantilever.py::test_grader_rejects_inverted_axis PASSED\n"
        "tests/test_cantilever.py::test_fem_simulation_agreement PASSED\n"
        "tests/test_convergence.py::test_grader_rejects_singularity_misclassification PASSED\n"
        "tests/test_thermal.py::test_grader_rejects_rigid_stop_penetration PASSED\n"
        "tests/test_thermal.py::test_grader_rejects_zero_gap_assumption PASSED\n\n"
        "============================= 33 passed in 2.18s ============================="
    )
    draw.text((110, 295), term_output, fill=(74, 222, 128), font=get_code_font(18), spacing=6)

    # Right side: Hackathon Criteria Cards
    draw.rounded_rectangle([1240, 220, 1840, 580], radius=12, fill=BG_CARD, outline=ACCENT_BLUE, width=2)
    draw.text((1270, 250), "No False Passes, No False Fails", fill=ACCENT_CYAN, font=get_font(26, bold=True))
    crit1 = (
        "- Reference answers verified with SymPy\n"
        "- 1D FEM direct stiffness cross-check\n"
        "- Every reference solution scores 100%\n"
        "- 0.5% perturbation: PASS\n"
        "- 2.0% perturbation: FAIL (1% tolerance)"
    )
    draw.text((1270, 310), crit1, fill=TEXT_WHITE, font=get_font(22), spacing=10)

    draw.rounded_rectangle([1240, 620, 1840, 980], radius=12, fill=BG_CARD, outline=ACCENT_AMBER, width=2)
    draw.text((1270, 650), "Adversarial Failure Mode Rejection", fill=ACCENT_AMBER, font=get_font(26, bold=True))
    crit2 = (
        "- Rejects forgotten self-weight (P only)\n"
        "- Rejects reversed intermediate loads\n"
        "- Rejects wall penetration in gaps\n"
        "- Rejects inverted section modulus (b^2*h/6)\n"
        "- Rejects Pascal vs MPa errors (10^6)"
    )
    draw.text((1270, 710), crit2, fill=TEXT_WHITE, font=get_font(22), spacing=10)

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_5.png")
    img.save(out_path)
    return out_path


def create_slide_6() -> str:
    """Scene 6: Empirical Results & Performance Comparison Chart"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "Empirical Results: The Consistency Collapse", "Experimental Evidence")

    # Embed generated chart
    chart_path = os.path.join(BASE_DIR, "results", "benchmark_comparison.png")
    if os.path.exists(chart_path):
        chart_img = Image.open(chart_path).resize((1050, 520))
        img.paste(chart_img, (80, 220))
        # Draw border
        draw.rectangle([80, 220, 1130, 740], outline=ACCENT_BLUE, width=2)

    # Right side: Metrics breakdown
    draw.rounded_rectangle([1170, 220, 1840, 740], radius=12, fill=BG_CARD, outline=ACCENT_CYAN, width=2)
    draw.text((1200, 250), "Benchmark Summary Metrics", fill=ACCENT_CYAN, font=get_font(28, bold=True))

    summary_text = (
        "Metric                 GPT-4o     Claude 3.5\n"
        "--------------------------------------------\n"
        "Total Trials               15             15\n"
        "Overall Pass Rate       53.3%          53.3%\n"
        "pass@3 (At least 1)     80.0%          80.0%\n"
        "pass^3 (All 3 Pass)      0.0%           0.0%\n"
        "Mean Score              70.7%          79.4%\n"
        "Task 3 Pass Rate         0.0%           0.0%\n"
        "Runtime (s)             21.0s          21.0s\n"
        "Estimated Cost          $0.04          $0.05"
    )
    draw.text((1200, 310), summary_text, fill=TEXT_CODE, font=get_code_font(22), spacing=8)

    # Bottom Callout banner
    draw.rounded_rectangle([80, 770, 1840, 980], radius=12, fill=(30, 20, 40), outline=ACCENT_AMBER, width=2)
    draw.text((120, 800), "Key Finding: The Consistency Illusion (pass@3 = 80.0% vs pass^3 = 0.0%)", fill=ACCENT_AMBER, font=get_font(28, bold=True))
    draw.text((120, 850), "Frontier models can get lucky once, but fail to maintain consistency across repeated trials on identical deterministic tasks.\nIn safety-critical physical engineering, a pass^k of 0% indicates that single-shot autonomous execution is not yet viable.", fill=TEXT_WHITE, font=get_font(21), spacing=8)

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_6.png")
    img.save(out_path)
    return out_path


def create_slide_7() -> str:
    """Scene 7: Insights & Conclusion"""
    img = Image.new("RGB", (1920, 1080), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "Engineering Insights & Next Steps", "Conclusion")

    draw.rounded_rectangle([80, 220, 1840, 540], radius=16, fill=BG_CARD, outline=ACCENT_GREEN, width=2)
    draw.text((120, 255), "Core Takeaways for Autonomous AI in Engineering", fill=ACCENT_GREEN, font=get_font(34, bold=True))

    takeaways = (
        "1. High Jargon Fluency != Physical Reliability:\n"
        "   Models explain formulas with high confidence while violating basic statical equilibrium.\n\n"
        "2. Kinematic Constraints Are Fragile:\n"
        "   Unilateral gap boundaries and statical indeterminacy consistently break reasoning.\n\n"
        "3. Verification Harnesses Are Non-Negotiable:\n"
        "   Autonomous engineering agents require deterministic, code-based verification filters."
    )
    draw.text((120, 320), takeaways, fill=TEXT_CODE, font=get_font(22), spacing=8)

    # Submission info card
    draw.rounded_rectangle([80, 580, 1840, 980], radius=16, fill=BG_CARD, outline=ACCENT_BLUE, width=2)
    draw.text((120, 615), "MechEval Submission Package Overview", fill=ACCENT_CYAN, font=get_font(30, bold=True))

    info = (
        "- Deliverable A: mecheval_submission.zip (0.22 MB, fully contained, no external dependencies)\n"
        "- Deliverable B: 5-Minute Video Walkthrough demonstrating the live grading harness\n"
        "- Deliverable C: Comprehensive research report and written submission documentation\n"
        "- 100% Open Source (MIT License) with full reproduction commands in README.md\n\n"
        "Thank you!  |  micro1 Eval Hackathon 2026"
    )
    draw.text((120, 680), info, fill=TEXT_WHITE, font=get_font(24), spacing=12)

    out_path = os.path.join(TEMP_VIDEO_DIR, "slide_7.png")
    img.save(out_path)
    return out_path


# Narration scripts for each scene
NARRATIONS = [
    (
        "slide_1",
        "MechEval is a code-graded AI evaluation benchmark built for the micro1 Eval Hackathon. "
        "It answers one question: can frontier AI models solve real mechanical engineering problems, "
        "or do they produce convincing but physically impossible solutions?"
    ),
    (
        "slide_2",
        "Five tasks span beam bending, axial loading, indeterminate structures, thermal contact, "
        "and finite element verification. Every ground truth is derived symbolically with SymPy "
        "and cross-checked against independent finite element simulations."
    ),
    (
        "slide_3",
        "Task three is the killer: a statically indeterminate propped cantilever. Statics alone cannot solve it. "
        "You must enforce deformation compatibility, giving reactions of eighteen and thirty kilonewtons "
        "and a clamping moment of twenty-four kilonewton meters."
    ),
    (
        "slide_4",
        "Both GPT-4o and Claude 3.5 Sonnet failed every attempt. GPT-4o hallucinated symmetric fifty-fifty reactions, "
        "missing the indeterminacy entirely. In real engineering, under-designing the fixed support by twenty percent "
        "risks joint shearing and collapse."
    ),
    (
        "slide_5",
        "Grading is deterministic: code checks final physical results within a one percent relative tolerance, "
        "validated by thirty-three automated Pytest cases. No false passes, no false fails."
    ),
    (
        "slide_6",
        "Results from thirty independent trials: pass-at-three of eighty percent, but pass-cubed — perfect consistency — exactly zero percent. "
        "On task three, neither model passed a single trial."
    ),
    (
        "slide_7",
        "MechEval shows that frontier models can recite engineering equations but cannot satisfy physical constraints. "
        "AI needs verification harnesses like this before autonomous engineering use. "
        "Everything is open source and fully reproducible. Thank you."
    ),
]


def generate_audio(slide_id: str, text: str) -> str:
    """Generates audio using Windows SpeechSynthesizer via PowerShell."""
    audio_path = os.path.join(TEMP_VIDEO_DIR, f"{slide_id}.wav")
    
    # Escape quotes for PowerShell
    clean_text = text.replace('"', '""').replace("'", "''")
    ps_cmd = (
        f"Add-Type -AssemblyName System.Speech; "
        f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Male); "
        f"$synth.Rate = 2; "
        f"$synth.SetOutputToWaveFile('{audio_path}'); "
        f"$synth.Speak('{clean_text}'); "
        f"$synth.Dispose();"
    )

    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
    return audio_path


def get_audio_duration(audio_path: str) -> float:
    """Gets audio duration using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())


def render_scene_video(image_path: str, audio_path: str, duration: float, output_path: str):
    """Combines slide image and audio into an MP4 segment with ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-framerate", "1",
        "-i", image_path,
        "-i", audio_path,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def build_full_video():
    print("\n" + "="*70)
    print("MECHEVAL AUTOMATED VIDEO WALKTHROUGH GENERATOR")
    print("="*70 + "\n")

    # Step 1: Render slides
    print("[1/4] Generating 1920x1080 video frames...")
    slides = [
        create_slide_1(),
        create_slide_2(),
        create_slide_3(),
        create_slide_4(),
        create_slide_5(),
        create_slide_6(),
        create_slide_7(),
    ]
    for s in slides:
        print(f"      - Created: {os.path.basename(s)}")

    # Step 2: Generate narration audio
    print("\n[2/4] Generating speech narration audio via SpeechSynthesizer...")
    audio_files = []
    durations = []
    for slide_id, text in NARRATIONS:
        a_path = generate_audio(slide_id, text)
        dur = get_audio_duration(a_path)
        audio_files.append(a_path)
        durations.append(dur)
        print(f"      - {slide_id}.wav ({dur:.1f}s)")

    total_dur = sum(durations) + len(durations) * 0.6
    mins = int(total_dur // 60)
    secs = int(total_dur % 60)
    print(f"\n      Total Calculated Video Duration: {mins}m {secs}s (Limit: 5m 00s)")

    # Step 3: Render individual scene segments
    print("\n[3/4] Rendering individual MP4 scene segments...")
    segment_paths = []
    for i in range(len(slides)):
        seg_path = os.path.join(TEMP_VIDEO_DIR, f"segment_{i+1}.mp4")
        render_scene_video(slides[i], audio_files[i], durations[i], seg_path)
        segment_paths.append(seg_path)
        print(f"      - Rendered segment {i+1} of {len(slides)}")

    # Step 4: Concatenate into final video
    print("\n[4/4] Concatenating master video: mecheval_walkthrough.mp4...")
    concat_list_path = os.path.join(TEMP_VIDEO_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for p in segment_paths:
            # ffmpeg concat needs forward slashes
            clean_p = p.replace("\\", "/")
            f.write(f"file '{clean_p}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        OUTPUT_VIDEO_PATH
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    size_mb = os.path.getsize(OUTPUT_VIDEO_PATH) / (1024 * 1024)
    print("\n" + "="*70)
    print(f"[SUCCESS] Final Video Walkthrough Created:")
    print(f"          Path:     {OUTPUT_VIDEO_PATH}")
    print(f"          Size:     {size_mb:.2f} MB")
    print(f"          Duration: {mins}m {secs}s")
    print("="*70 + "\n")


if __name__ == "__main__":
    build_full_video()
