export const CATEGORIES = [
  {
    id: 'medical',
    name: 'Medical Effects',
    desc: 'What each med pen actually does.',
    enabled: true,
    ready: true,
  },
  {
    id: 'survival',
    name: 'Survival Warnings',
    desc: 'Cold, heat, oxygen and injury warnings get advice.',
    enabled: true,
    ready: true,
  },
  {
    id: 'mission_rewards',
    name: 'Mission Rewards',
    desc: 'Payout on every contract description.',
    enabled: true,
    ready: true,
  },
  {
    id: 'ship_specs',
    name: 'Ship Basics',
    desc: 'Crew and class on ship descriptions.',
    enabled: true,
    ready: true,
  },
  {
    id: 'components',
    name: 'Components',
    desc: 'Shield HP/regen and quantum speed on ship items.',
    enabled: true,
    ready: true,
  },
  {
    id: 'weapons',
    name: 'Weapons',
    desc: 'Fire rate, magazine, damage and DPS on guns.',
    enabled: true,
    ready: true,
  },
  {
    id: 'armor',
    name: 'Armor Ratings',
    desc: 'Temperature range on every armor piece and undersuit.',
    enabled: true,
    ready: true,
  },
];

export const SAMPLE_STRINGS = [
  {
    key: 'mission_Highpoint_Deliver_name',
    category: 'Missions',
    stock: 'Deliver Shipment',
    enhanced: 'Deliver Shipment  ·  Area18 › Lorville  ·  [ +250 Hurston Sec ]',
    status: 'enhanced',
  },
  {
    key: 'vehicle_Desc_RSI_Constellation_Andromeda',
    category: 'Ships',
    stock: 'A versatile multi-crew freighter trusted across the empire.',
    enhanced:
      'A versatile multi-crew freighter trusted across the empire.\nSCM 215 m/s · Crew 4 · Cargo 96 SCU',
    status: 'enhanced',
  },
  {
    key: 'item_Desc_SHLD_Basilisk_S2',
    category: 'Ship Items',
    stock: 'A reliable size 2 shield generator.',
    enhanced: 'A reliable size 2 shield generator.\nHP 8,200 · Regen 420/s · Downtime 12s',
    status: 'enhanced',
  },
  {
    key: 'item_Name_WEAP_Gatling_S3',
    category: 'Ship Items',
    stock: 'Gatling Repeater',
    enhanced: 'Gatling Repeater',
    status: 'unmodified',
  },
  {
    key: 'commodity_Desc_Titanium',
    category: 'Commodities',
    stock: 'A lightweight structural metal in constant demand.',
    enhanced:
      'A lightweight structural metal in constant demand.\n[RS 1420]  ·  Refined at: ArcCorp Mining',
    status: 'modified',
  },
  {
    key: 'mobiglas_ui_Contracts_Header',
    category: 'Other',
    stock: 'Contracts',
    enhanced: 'Contracts',
    status: 'unmodified',
  },
];
