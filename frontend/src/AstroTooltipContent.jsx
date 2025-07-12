import React from "react";
import definitions from "./astro_definitions.json";

function normalizeLabelPart(part) {
  if (!part) return part;
  // Always coerce to string before trim
  const str = String(part);
  if (str === "ASC") return "AC";
  if (str === "DSC") return "DC";
  if (str === "IC") return "IC";
  if (str === "MC") return "MC";
  return str.trim();
}

function getFullDef(part) {
  if (!part) return null;
  const key = normalizeLabelPart(part);
  return (
    getDef("planets", key) ||
    getDef("asteroids", key) ||
    getDef("lunarPoints", key) ||
    getDef("hermeticLots", key) ||
    getDef("angles", key) ||
    getDef("aspects", key) ||
    getDef("aspectLines", key) ||
    getDef("fixedStars", key) ||
    null
  );
}

function getDef(type, key) {
  if (!key) return null;
  return definitions[type] && definitions[type][key] ? definitions[type][key] : null;
}

const renderDefLine = (label, def) => (
  <React.Fragment>
    <b>{label}</b>
    {def && <span style={{ fontStyle: "italic", color: "#888", marginLeft: 4 }}>– {def}</span>}
  </React.Fragment>
);

function parseLabel(label) {
  if (!label) return [];
  let clean = label.replace(/\s*\(.*\)$/, "").trim();
  const aspects = ["conjunct", "opposite", "square", "trine", "sextile", "quincunx"];
  let parts = clean.split(" ");
  if (parts.length === 3 && aspects.includes(parts[1])) {
    return [parts[0], parts[1], parts[2]];
  }
  return parts;
}

// --- Helper to extract the best id for house/sign lookup ---
function getFeatureId(feat) {
  if (!feat || !feat.properties) return null;
  const p = feat.properties;
  return (
    p.planet_id ||
    p.body_key ||
    p.star_id ||
    p.star_key ||
    p.body ||
    p.planet ||
    p.star ||
    p.name ||
    null
  );
}

function capitalize(str) {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function getOrdinalSuffix(num) {
  const j = num % 10;
  const k = num % 100;
  if (j === 1 && k !== 11) return `${num}st`;
  if (j === 2 && k !== 12) return `${num}nd`;
  if (j === 3 && k !== 13) return `${num}rd`;
  return `${num}th`;
}

// Helper function to get human-readable layer name
function getLayerDisplayName(layerName) {
  switch (layerName) {
    case 'natal': return 'Natal';
    case 'CCG': return 'CCG';
    case 'transit': return 'Transit';
    case 'HD_DESIGN': return 'Design';
    default: return layerName || 'Natal';
  }
}

const AstroTooltipContent = ({ feat, label }) => {
  if (!feat || !feat.properties) return <b>{label}</b>;
  const { planet, type, star, planets, angles } = feat.properties;
  const lines = [];

  // Get layer information
  const layerName = feat.layerName || 'natal';
  const layerDisplayName = getLayerDisplayName(layerName);
  
  // Main label with layer indicator
  const labelWithLayer = `${layerDisplayName} ${label}`;
  lines.push(<div key="main" style={{ marginBottom: 4 }}><b>{labelWithLayer}</b></div>);
  const labelParts = parseLabel(label);
  const alreadyRendered = new Set();

  // Collect planet/body definitions first
  const planetDefinitions = [];
  const houseDefinitions = [];
  const signDefinitions = [];
  const aspectDefinitions = [];

  // --- 1. PLANET/BODY DEFINITIONS ---
  // Always try to render the definition for the feature id (for multi-word features, lots, etc.)
  const featureId = getFeatureId(feat);
  let idDefRendered = false;
  if (featureId && getFullDef(featureId) && !alreadyRendered.has(featureId)) {
    planetDefinitions.push(renderDefLine(featureId, getFullDef(featureId)));
    alreadyRendered.add(featureId);
    idDefRendered = true;
  }
  // If id is not a string key in definitions, also try display name (planet/body/star)
  const displayName = feat.properties.planet || feat.properties.body || feat.properties.star || feat.properties.name;
  if (
    displayName &&
    (!idDefRendered || featureId !== displayName) &&
    getFullDef(displayName) &&
    !alreadyRendered.has(displayName)
  ) {
    planetDefinitions.push(renderDefLine(displayName, getFullDef(displayName)));
    alreadyRendered.add(displayName);
  }

  // Parans: show both planets and both angles, no duplicates
  if ((type === "paran" || feat.properties.category === "parans") && Array.isArray(feat.properties.source_lines)) {
    const sourceLines = feat.properties.source_lines;
    sourceLines.forEach(sourceLine => {
      if (sourceLine && sourceLine.includes("_")) {
        const planetName = sourceLine.split("_")[0].replace(/ (CCG|Transit|HD)$/g, "");
        if (planetName && getFullDef(planetName) && !alreadyRendered.has(planetName)) {
          planetDefinitions.push(renderDefLine(planetName, getFullDef(planetName)));
          alreadyRendered.add(planetName);
        }
        const angleName = sourceLine.split("_")[1];
        if (angleName && getFullDef(angleName) && !alreadyRendered.has(angleName)) {
          aspectDefinitions.push(renderDefLine(angleName, getFullDef(angleName)));
          alreadyRendered.add(angleName);
        }
      }
    });
  } else if (type === "paran" && Array.isArray(planets)) {
    // fallback for old-style parans
    planets.forEach((p) => {
      if (p && getFullDef(p) && !alreadyRendered.has(p)) {
        planetDefinitions.push(renderDefLine(p, getFullDef(p)));
        alreadyRendered.add(p);
      }
    });
    if (Array.isArray(angles)) {
      angles.forEach((a) => {
        if (a && getFullDef(a) && !alreadyRendered.has(a)) {
          aspectDefinitions.push(renderDefLine(a, getFullDef(a)));
          alreadyRendered.add(a);
        }      });
    }
  }

  // Fixed stars: always show definition
  if ((type === "fixed_star" || type === "star" || star)) {
    const starName = star || planet;
    if (starName && getFullDef(starName) && !alreadyRendered.has(starName)) {
      planetDefinitions.push(renderDefLine(starName, getFullDef(starName)));
      alreadyRendered.add(starName);
    }
  }

  // Handle remaining planets from label parsing
  labelParts.forEach((part) => {
    if (!alreadyRendered.has(part) && getFullDef(part)) {
      // Check if it's a planet/body/asteroid
      if (getDef("planets", part) || getDef("asteroids", part) || getDef("lunarPoints", part) || getDef("hermeticLots", part) || getDef("fixedStars", part)) {
        planetDefinitions.push(renderDefLine(part, getFullDef(part)));
        alreadyRendered.add(part);
      }
    }
  });

  // Multi-word planet/body handling
  for (let len = labelParts.length; len >= 2; len--) {
    for (let start = 0; start <= labelParts.length - len; start++) {
      const joined = labelParts.slice(start, start + len).join(" ");
      if (getFullDef(joined) && !alreadyRendered.has(joined)) {
        // Check if it's a planet/body/asteroid
        if (getDef("planets", joined) || getDef("asteroids", joined) || getDef("lunarPoints", joined) || getDef("hermeticLots", joined) || getDef("fixedStars", joined)) {
          planetDefinitions.push(renderDefLine(joined, getFullDef(joined)));
          alreadyRendered.add(joined);
          for (let k = start; k < start + len; k++) {
            alreadyRendered.add(labelParts[k]);
          }
        }
      }
    }
  }

  // --- 2. HOUSE DEFINITIONS ---
  if (feat.properties.house != null) {
    const houseDef = getDef("houses", String(feat.properties.house));
    if (houseDef) {
      houseDefinitions.push(
        renderDefLine(
          `${getOrdinalSuffix(Number(feat.properties.house))} house`,
          houseDef
        )
      );
    }
  }

  // --- 3. ZODIAC SIGN DEFINITIONS ---
  if (feat.properties.sign != null) {
    const signDef = getDef("zodiacSigns", String(feat.properties.sign));
    if (signDef) {
      signDefinitions.push(renderDefLine(String(feat.properties.sign), signDef));
    }
  }

  // --- 4. ASPECT/LINE TYPE DEFINITIONS ---
  // Aspect and multi-word logic
  if (labelParts.length >= 3) {
    const aspect = labelParts[labelParts.length - 2];
    const angle = labelParts[labelParts.length - 1];
    
    // Aspect line
    const aspectLineKey = `${capitalize(aspect)} ${normalizeLabelPart(angle)}`;
    if (getDef("aspectLines", aspectLineKey) && !alreadyRendered.has(aspectLineKey)) {
      aspectDefinitions.push(renderDefLine(aspectLineKey, getDef("aspectLines", aspectLineKey)));
      alreadyRendered.add(aspectLineKey);
      alreadyRendered.add(aspect);
      alreadyRendered.add(angle);
    } else {
      if (!alreadyRendered.has(aspect) && getFullDef(aspect)) {
        aspectDefinitions.push(renderDefLine(aspect, getFullDef(aspect)));
        alreadyRendered.add(aspect);
      }
      if (!alreadyRendered.has(angle) && getFullDef(angle)) {
        aspectDefinitions.push(renderDefLine(angle, getFullDef(angle)));
        alreadyRendered.add(angle);
      }
    }
  }

  // Handle remaining aspects/angles from label parsing
  labelParts.forEach((part) => {
    if (!alreadyRendered.has(part) && getFullDef(part)) {
      // Check if it's an aspect or angle
      if (getDef("aspects", part) || getDef("angles", part) || getDef("aspectLines", part)) {
        aspectDefinitions.push(renderDefLine(part, getFullDef(part)));
        alreadyRendered.add(part);
      }
    }
  });

  // Add all definitions in order: Planet, House, Zodiac, Aspect/Line
  lines.push(...planetDefinitions);
  lines.push(...houseDefinitions);
  lines.push(...signDefinitions);
  lines.push(...aspectDefinitions);

  return <div style={{ lineHeight: 1.4 }}>{lines.map((line, index) => <div key={index} style={{ marginBottom: 2 }}>{line}</div>)}</div>;
};

export default AstroTooltipContent;
