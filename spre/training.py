"""SPRE training set: historically confirmed institutional failures only.

Each prototype is a *structural shape* taken from a case that a government
or official inquiry later acknowledged as a failure. SPRE compares new
inputs to these shapes. It never identifies a new case as that event,
never names a living person as guilty, and never asserts conspiracy.

Author: Aziel Eliab, 2026. Apache-2.0.
"""

from __future__ import annotations

# Training cases are annotated field records. Vectors are computed by the
# engine so training and testing share one scorer.

TRAINING_CASES: tuple[dict, ...] = (
    {
        "id": "tuskegee-usphs",
        "confirmed_by": "U.S. government acknowledgment (1972 exposure; 1997 apology)",
        "official": (
            "Official health narrative: a treatment study for rural patients "
            "under public health supervision."
        ),
        "internal": (
            "Internal protocol withheld treatment, tracked untreated disease, "
            "and instructed staff not to give the standard cure."
        ),
        "physics": "Independent medical review later showed non-treatment was the actual protocol.",
        "coroner": "In-house public-health clinicians wrote the medical notes.",
        "authority": "The same public-health office both studied and oversaw the men.",
        "evidence": [
            "later independent medical review",
            "surviving protocol memos after disclosure",
        ],
        "destroyed": ["early adverse notes never filed with the families"],
        "victim_framing": "Patients were described as noncompliant and lucky to have any care.",
        "records": "Key consent and treatment logs were missing or never filed.",
        "contemporaneous": "",
        "note": "Structural shape only. Not an identification of any new case.",
    },
    {
        "id": "cointelpro-church",
        "confirmed_by": "U.S. Senate Church Committee (1975–1976)",
        "official": (
            "Official narrative: ordinary lawful investigations of threats."
        ),
        "internal": (
            "Internal program disrupted lawful groups, used anonymous smears, "
            "and hid the program from the stated mission."
        ),
        "physics": "",
        "coroner": "",
        "authority": "The investigating office certified its own legality.",
        "evidence": ["Church Committee documentary record"],
        "destroyed": ["files shredded when the program was exposed"],
        "victim_framing": "Targets were framed as reckless extremists who brought scrutiny on themselves.",
        "records": "Paper trail was shredded; contemporaneous logs had gaps.",
        "contemporaneous": "",
        "note": "Structural shape only. Not an identification of any new case.",
    },
    {
        "id": "iran-contra",
        "confirmed_by": "Tower Commission and U.S. congressional investigations (1987)",
        "official": (
            "Official narrative: no third-country arms diversion and no extra "
            "legal channel."
        ),
        "internal": (
            "Internal channel moved arms proceeds off-book and wrote a second "
            "story that contradicted the public line."
        ),
        "physics": "",
        "coroner": "",
        "authority": "The same offices that ran the channel also briefed oversight.",
        "evidence": ["Tower Commission record", "later contemporaneous notes that survived"],
        "destroyed": ["shredded diversion papers", "overwritten message traffic"],
        "victim_framing": "",
        "records": "Chain of custody on cables was broken; pages were shredded.",
        "contemporaneous": "A few contemporaneous notes survived outside the official file.",
        "note": "Structural shape only. Not an identification of any new case.",
    },
    {
        "id": "flint-water",
        "confirmed_by": "State and federal acknowledgments; independent water chemistry",
        "official": (
            "Official narrative: the switched water was safe to drink and met rules."
        ),
        "internal": (
            "Internal emails treated resident complaints as overreaction while "
            "corrosion control was not applied."
        ),
        "physics": (
            "Independent lab chemistry found lead and corrosion far above the "
            "official safety claim."
        ),
        "coroner": "City and state health offices issued the medical-sounding all-clear.",
        "authority": "The same authorities certified the water and investigated complaints.",
        "evidence": ["independent university water tests", "resident samples"],
        "destroyed": ["early test sets that failed were not kept in the public file"],
        "victim_framing": "Residents were called hysterical and told their lifestyle explained the rash.",
        "records": "Some early failing tests were unlogged in the public record.",
        "contemporaneous": "Resident contemporaneous samples contradicted the later official line.",
        "note": "Structural shape only. Not an identification of any new case.",
    },
    {
        "id": "thalidomide-regulatory",
        "confirmed_by": "Later regulatory acknowledgments of approval-safety failure",
        "official": (
            "Official narrative: the sedative was safe for pregnant patients."
        ),
        "internal": (
            "Internal safety files lacked the expected birth-defect trials and "
            "treated the gap as unimportant."
        ),
        "physics": "Independent clinical observations later showed a physical harm pattern.",
        "coroner": "",
        "authority": "The approving office also explained away early harm reports.",
        "evidence": ["later independent clinical series"],
        "destroyed": ["unexamined adverse reports sat outside the approval file"],
        "victim_framing": "Mothers were implied to have other lifestyle causes.",
        "records": "Required safety trials were missing from the approval paper trail.",
        "contemporaneous": "",
        "note": "Structural shape only. Not an identification of any new case.",
    },
)

# Negative-control shapes used only in tests and doctor. They are NOT
# training. Low SSI is required (anti-apophenia).
NEGATIVE_CONTROLS: tuple[dict, ...] = (
    {
        "id": "neg-open-accident",
        "official": (
            "A car left the wet road at night. Speed was over the limit. "
            "The driver survived with a broken arm. Skid marks match."
        ),
        "internal": (
            "A car left the wet road at night. Speed was over the limit. "
            "The driver survived with a broken arm. Skid marks match."
        ),
        "physics": (
            "A car left the wet road at night. Speed was over the limit. "
            "Skid marks match the exit path."
        ),
        "coroner": "An independent hospital doctor treated the broken arm.",
        "authority": "Traffic police measured the marks. They are not the hospital.",
        "evidence": ["skid-mark photos", "weather log", "independent hospital note"],
        "destroyed": [],
        "victim_framing": "The driver is described as injured. Speed is a measured fact only.",
        "records": "Full contemporaneous log, photos kept in an open file.",
        "contemporaneous": "On-scene notes written that night match the later file.",
    },
    {
        "id": "neg-software-login",
        "official": "The login button is blue and says submit. The form sends name and password.",
        "internal": "The login button is blue and says submit. The form sends name and password.",
        "physics": "",
        "coroner": "",
        "authority": "",
        "evidence": ["screenshot", "request log"],
        "destroyed": [],
        "victim_framing": "",
        "records": "Commit log and test receipt are present.",
        "contemporaneous": "The same-day commit message matches the request log.",
    },
    {
        "id": "neg-empty",
        "official": "",
        "internal": "",
        "physics": "",
        "coroner": "",
        "authority": "",
        "evidence": [],
        "destroyed": [],
        "victim_framing": "",
        "records": "",
        "contemporaneous": "",
    },
)
