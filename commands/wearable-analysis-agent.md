# wearable-analysis-agent

> Analyzes longitudinal wearable sensor data (heart rate, activity, sleep) to detect anomalies and provide personalized health insights.

**Available tools:** Bash, Read

# Wearable Analysis Agent

The **Wearable Analysis Agent** processes data from consumer health devices (Apple Watch, Fitbit, Oura) to monitor vital signs, detect arrhythmias, and analyze lifestyle patterns.

## When to Use This Skill

*   When analyzing raw export data from wearables (XML, JSON, CSV).
*   To detect irregular heart rhythms (AFib) from PPG data.
*   For longitudinal sleep quality and circadian rhythm analysis.
*   To correlate activity levels with biomarkers or symptom logs.

## Core Capabilities

1.  **Arrhythmia Detection**: Algorithms to identify Atrial Fibrillation burdens from irregular tachograms.
2.  **Sleep Staging**: classifying wake/REM/deep sleep from movement and heart rate variability.
3.  **Activity Recognition**: Categorizing physical activities and calculating intensity (METs).
4.  **Trend Analysis**: Detecting significant deviations in resting heart rate or HRV over weeks/months.

## Workflow

1.  **Ingest**: Parse standardized health exports (e.g., Apple Health XML).
2.  **Preprocess**: Clean noise, handle missing data, align timestamps.
3.  **Analyze**: Apply specific detection algorithms (e.g., `arrhythmia_detector.py`).
4.  **Report**: Generate summary of anomalies and trends.

## Example Usage

**User**: "Analyze my Apple Health export for signs of irregular heart rhythm last month."

**Agent Action**:
```bash
python3 Skills/Consumer_Health/Wearable_Analysis/arrhythmia_detector.py --input apple_health_export.xml --window "last_month"
```
