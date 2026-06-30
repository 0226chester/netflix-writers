"""
This module contains a function to write a CSV file of dramatic situations.

based on Polti's 36 dramatic situations. The CSV file will have three
columns: "Number", "Situation", and "Description". Each row corresponds to
one of the 36 dramatic situations, with its number, name, and a brief
description. The output path for the CSV file can be specified through an
environment variable or defaults to "situations.csv" in the current directory.
"""

import csv
import logging
import os
from pathlib import Path

from netflix.const import DATA_DIR

POLTI_DIR = os.path.join(DATA_DIR, "polti")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def write_situations_csv(output_path: Path) -> None:
    """
    Writes a CSV file containing dramatic situations.

    Args:
        output_path (Path): Path to output CSV file.
    """

    rows = [
        (1, "Supplication", "A suppliant appeals to a power in authority for deliverance from a persecutor."),
        (2, "Deliverance", "A rescuer saves an unfortunate person from a threatener."),
        (
            3,
            "Crime Pursued by Vengeance",
            "An avenger seeks justice against a criminal whose crime would otherwise go unpunished.",
        ),
        (4, "Vengeance Taken for Kin Upon Kin", "One kinsman avenges a victim against another guilty kinsman."),
        (5, "Pursuit", "A fugitive flees from punishment."),
        (
            6,
            "Disaster",
            "A defeated power falls before a victorious enemy or learns of its downfall through a messenger.",
        ),
        (7, "Falling Prey to Cruelty or Misfortune", "An unfortunate person suffers under misfortune or oppression."),
        (8, "Revolt", "Conspirators plot against a tyrant."),
        (
            9,
            "Daring Enterprise",
            "A bold leader undertakes a dangerous quest against an adversary to obtain an objective.",
        ),
        (10, "Abduction", "An abductor takes someone away from their guardian."),
        (11, "The Enigma", "A seeker attempts to solve a problem posed by an interrogator."),
        (
            12,
            "Obtaining",
            "A solicitor struggles to obtain something withheld by an adversary, or an arbitrator settles competing claims.",
        ),
        (13, "Enmity of Kin", "Hostility and conflict arise between relatives."),
        (14, "Rivalry of Kin", "Relatives compete for the favor of a desired person or object."),
        (15, "Murderous Adultery", "Two adulterers conspire to kill a betrayed spouse."),
        (16, "Madness", "A madman harms a victim under the influence of insanity."),
        (
            17,
            "Fatal Imprudence",
            "Carelessness or ignorance causes harm to a victim or the loss of something valuable.",
        ),
        (18, "Involuntary Crimes of Love", "Lovers unknowingly violate a taboo, and the truth is revealed to them."),
        (19, "Slaying of Kin Unrecognized", "A person kills a relative without recognizing their identity."),
        (20, "Self-Sacrifice for an Ideal", "A hero sacrifices someone or something in service of an ideal."),
        (21, "Self-Sacrifice for Kin", "A hero sacrifices for the benefit of a relative."),
        (22, "All Sacrificed for Passion", "A lover sacrifices everything for the object of their passion."),
        (23, "Necessity of Sacrificing Loved Ones", "A hero harms a loved one because circumstances demand it."),
        (
            24,
            "Rivalry of Superior vs. Inferior",
            "An inferior rival overcomes a superior rival to win the object of desire.",
        ),
        (25, "Adultery", "Two adulterers deceive and conspire against a spouse."),
        (26, "Crimes of Love", "Lovers knowingly violate a taboo through their relationship."),
        (27, "Discovery of the Dishonour of a Loved One", "Someone uncovers the wrongdoing of a person they love."),
        (28, "Obstacles to Love", "Lovers struggle together against forces that keep them apart."),
        (29, "An Enemy Loved", "A person loves someone regarded as an enemy by others."),
        (30, "Ambition", "An ambitious person pursues a coveted goal despite opposition."),
        (31, "Conflict with a God", "A mortal comes into conflict with an immortal power."),
        (32, "Mistaken Jealousy", "False appearances or deception provoke jealousy."),
        (
            33,
            "Erroneous Judgment",
            "A mistaken person condemns the wrong individual because of deception or misunderstanding.",
        ),
        (34, "Remorse", "A culprit struggles with guilt while their actions are examined or questioned."),
        (35, "Recovery of a Lost One", "A seeker finds someone who was lost."),
        (36, "Loss of Loved Ones", "A person witnesses or endures the killing of a loved one."),
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Number", "Situation", "Description"])
        writer.writerows(rows)

    logger.info("CSV written to: %s", output_path)


def main():
    path = Path(os.path.join(POLTI_DIR, "situations.csv"))
    write_situations_csv(path)
    logger.info("-" * 40)


if __name__ == "__main__":
    main()
