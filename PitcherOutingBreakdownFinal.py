import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Set the pitcher name and load csv
pitcherName = 'Johnson, David'
data = pd.read_csv('TrackmanData.csv')

# Get data for pitcher and drop rows with missing values
df = data[data['Pitcher'] == pitcherName]
dfPlotted = df.dropna(subset=['HorzBreak', 'InducedVertBreak', 'RelSide', 'RelHeight', 'PlateLocSide', 'PlateLocHeight'])

# Set up functions for additional stats
def getWhiffPerc(dataframe):
    totalSwings = len(dataframe[dataframe['PitchCall'].isin(['StrikeSwinging', 'InPlay', 'FoulBallNotFieldable', 'FoulBallFieldable'])])
    whiffPitches = len(dataframe[dataframe['PitchCall'] == 'StrikeSwinging'])
    whiffPercentage = (whiffPitches / totalSwings) * 100 if totalSwings > 0 else 0
    return whiffPercentage

def getZonePerc(dataframe):
    inZone = (dataframe['PlateLocHeight'].between(1.5, 3.5)) & (dataframe['PlateLocSide'].between(-0.71, 0.71))
    return (inZone.sum() / len(dataframe)) * 100

def getChasePerc(dataframe):
    outsideZone = ~((dataframe['PlateLocHeight'].between(1.5, 3.5)) & (dataframe['PlateLocSide'].between(-0.71, 0.71)))
    chaseSwings = dataframe[outsideZone & dataframe['PitchCall'].isin(['StrikeSwinging', 'InPlay', 'FoulBallNotFieldable', 'FoulBallFieldable'])]
    totalChasePitches = len(dataframe[outsideZone])
    chasePercentage = (len(chaseSwings) / totalChasePitches) * 100 if totalChasePitches > 0 else 0
    return chasePercentage

# Create figure with subplots
fig = plt.figure(figsize=(16, 11))
gridSpec = fig.add_gridspec(2, 3, height_ratios=[2.5, 1], hspace=0.5, wspace=0.35,
                            top=0.90, bottom=0.15, left=0.06, right=0.96)

# Get opponent name and Date for Title
date = df['Date'].iloc[0] if not df['Date'].empty else 'Unknown Date'
opponent = df['BatterTeam'].iloc[0] if not df['BatterTeam'].empty else 'Unknown Opponent'

# Add main title
fig.suptitle(f'{pitcherName} vs. {opponent}, {date}', fontsize=16, fontweight='bold', y=0.96)

# Colors for the pitches
colors = {
    'Four-Seam': 'red',
    'Fastball': 'red',
    'Slider': 'gold',
    'Curveball': 'blue',
    'Changeup': 'green',
    'ChangeUp': 'green',
    'Cutter': '#933F2C',
    'Sinker': 'orange',
    'Splitter': 'teal'
}
colorList = [colors.get(pitchType, 'gray') for pitchType in dfPlotted['AutoPitchType']]

# Scatter plot 1 - Pitch Movement
ax1 = fig.add_subplot(gridSpec[0, 0])
xData1 = dfPlotted['HorzBreak'].values
yData1 = dfPlotted['InducedVertBreak'].values
ax1.scatter(xData1, yData1, c=colorList, alpha=0.9, s=90, linewidth=0.5, edgecolors='k')
ax1.set_title('Pitch Movement Profile', fontsize=12, pad=10)
ax1.set_xlabel('Horizontal Break', fontsize=10)
ax1.set_ylabel('Induced Vertical Break', fontsize=10)
ax1.set_xlim(-30, 30)
ax1.set_ylim(-30, 30)
ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
ax1.invert_xaxis()
ax1.set_aspect("equal", adjustable="box")
ax1.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.8)
ax1.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.8)

# Scatter plot 2 - Release Point
ax2 = fig.add_subplot(gridSpec[0, 1])
xData2 = dfPlotted['RelSide'].values
yData2 = dfPlotted['RelHeight'].values
ax2.scatter(xData2, yData2, c=colorList, alpha=0.6, s=70, linewidth=0.5, edgecolors='k')
ax2.set_title('Pitcher Release Point', fontsize=12, pad=10)
ax2.set_xlabel('Release Side (ft)', fontsize=10)
ax2.set_ylabel('Release Height (ft)', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(3.5, -3.5)
ax2.set_ylim(0, 7.5)

# Scatter plot 3 - Pitch Locations
ax3 = fig.add_subplot(gridSpec[0, 2])
xData3 = dfPlotted['PlateLocSide'].values
yData3 = dfPlotted['PlateLocHeight'].values
ax3.scatter(xData3, yData3, c=colorList, s=70, linewidth=0.5, edgecolors='k')
ax3.set_xlim(-3, 3)
ax3.set_ylim(-1, 6)
ax3.set_aspect("equal", adjustable="box")
ax3.set_title('Pitch Locations', fontsize=12, pad=10)
ax3.set_xlabel('Horizontal Location (ft)', fontsize=10)
ax3.set_ylabel('Vertical Location (ft)', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.invert_xaxis()

# Draw Strike Zone
szXMin, szXMax = -0.71, 0.71
szYMin, szYMax = 1.5, 3.5
ax3.plot([szXMin, szXMax, szXMax, szXMin, szXMin],
         [szYMin, szYMin, szYMax, szYMax, szYMin],
         color='blue', linewidth=2)
ax3.fill_between([szXMin, szXMax], szYMin, szYMax, color='skyblue', alpha=0.3)

# TABLE: Pitch Statistics
tableColumns = ['Pitch Name', 'Count', 'Velocity', 'IVB', 'HB', 'Spin', 'hRel', 'vRel', 'Ext', 'Whiff%', 'Zone%', 'Chase%']
pitchStats = []
groupedStats = df.groupby('AutoPitchType')

# Get stats for each pitch type
for pitchType, group in groupedStats:
    stats = {
        'Pitch Name': pitchType,
        'Count': len(group),
        'Velocity': round(group['RelSpeed'].mean(), 1),
        'IVB': round(group['InducedVertBreak'].mean(), 1),
        'HB': round(group['HorzBreak'].mean(), 1),
        'Spin': round(group['SpinRate'].mean()),
        'hRel': round(group['RelSide'].mean(), 2),
        'vRel': round(group['RelHeight'].mean(), 2),
        'Ext': round(group['Extension'].mean(), 2),
        'Whiff%': round(getWhiffPerc(group), 1),
        'Zone%': round(getZonePerc(group), 1),
        'Chase%': round(getChasePerc(group), 1)
    }
    pitchStats.append(stats)

if pitchStats:
    resultDf = pd.DataFrame(pitchStats)
    resultDf = resultDf[tableColumns]
    resultDf = resultDf.fillna('-')

    # Calculate avg values for totals row
    totalCount = resultDf['Count'].sum()
    avgHRel = round(df['RelSide'].mean(), 2) if 'RelSide' in df.columns else '-'
    avgVRel = round(df['RelHeight'].mean(), 2) if 'RelHeight' in df.columns else '-'
    avgExt = round(df['Extension'].mean(), 2) if 'Extension' in df.columns else '-'
    whiff = round(getWhiffPerc(df), 1)
    zone = round(getZonePerc(df), 1)
    chase = round(getChasePerc(df), 1)

    totalsRow = pd.DataFrame([{
        'Pitch Name': 'Total',
        'Count': totalCount,
        'Velocity': '-',
        'IVB': '-',
        'HB': '-',
        'Spin': '-',
        'hRel': avgHRel,
        'vRel': avgVRel,
        'Ext': avgExt,
        'Whiff%': whiff,
        'Zone%': zone,
        'Chase%': chase
    }])

    resultDf = pd.concat([resultDf, totalsRow], ignore_index=True)

    rowLabels = resultDf['Pitch Name'].astype(str).tolist()
    tableCols = tableColumns[1:]
    cellText = resultDf[tableCols].astype(str).values.tolist()

    axTable = fig.add_subplot(gridSpec[1, :])
    axTable.axis('off')

    table = axTable.table(
        cellText=cellText,
        rowLabels=rowLabels,
        colLabels=tableCols,
        cellLoc='center',
        loc='center',
        colWidths=[0.08, 0.09, 0.08, 0.08, 0.09, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
    )

    table.scale(1.0, 2.5)
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    # Color data rows with pitch type colors
    for i in range(len(rowLabels)):
        pitchType = rowLabels[i]
        rowColor = colors.get(pitchType, 'white')
        # Lighten the color for data cells
        try:
            rgb = mcolors.to_rgb(rowColor)
            lightColor = tuple(min(1.0, c + 0.7) for c in rgb)
        except:
            lightColor = 'white'

        # Style row labels with the pitch color
        table[(i + 1, -1)].set_facecolor(rowColor)
        table[(i + 1, -1)].set_text_props(weight='bold', color='black')

        # Make data cells with lighter version
        for j in range(len(tableCols)):
            table[(i + 1, j)].set_facecolor(lightColor)
            table[(i + 1, j)].set_text_props(color='black')

fig.text(0.5, 0.01, "Source: TrackMan Data | Created by Charlie Capretta | All Plots From Umpire View",
         ha='center', fontsize=10, color='gray')

plt.show()