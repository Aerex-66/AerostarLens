import os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIVE = r"D:\Star Citizen Leftovers\StarCitizen\LIVE"
CPROG = r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE"
roots = [p for p in (LIVE, CPROG) if os.path.isdir(p)]
logs = []
for r in roots:
    g = os.path.join(r, "Game.log")
    if os.path.isfile(g):
        logs.append(g)
    logs += sorted(glob.glob(os.path.join(r, "logbackups", "*.log")), key=os.path.getmtime)[-4:]
print("scanning:", len(logs), "logs from", roots)

KNOWN = re.compile(r"AttachmentReceived|Add Inventory Management Move|Query Inventory|Inventory Token Flow|"
                   r"Request Personal Inventory Data|Inventory Mgmt|Player Inventory Request|Inventory Request Completed|"
                   r"Remove Inventory Container|EquipItem|Update Inventory|CVARS|StatObjLoad|Team_|SCTransportCarriage|"
                   r"Player (entered|exited) carriage|data carriage")

FAMS = {
    "commodity/cargo/SCU": re.compile(r"commodity|\bSCU\b|CargoManifest|kiosk.*(sell|buy)|SellableCommod", re.I),
    "shop buy/sell": re.compile(r"ShopPurchase|BuyRequest|SellRequest|Purchase (Complete|Request)|Transaction|shop.*(bought|sold)", re.I),
    "crafting/blueprint": re.compile(r"blueprint|crafting|\bcraft(ed|ing)?\b|Recipe", re.I),
    "kills/combat": re.compile(r"Actor Death|CActor::Kill|IncapAgent|Corpse", re.I),
    "harvest/salvage/mining": re.compile(r"Harvest|Salvage|Mining|Extraction|FractureRock", re.I),
    "missions accepted/done": re.compile(r"Mission (Accepted|Completed|Failed|Objective)|ContractState|MissionEnd", re.I),
    "rep/standing events": re.compile(r"Reputation(Gain|Award|Change)|StandingChanged", re.I),
    "money/wallet": re.compile(r"aUEC|WalletBalance|CurrencyChange|MicroSCU", re.I),
}

counts = {k: 0 for k in FAMS}
samples = {k: [] for k in FAMS}
unknown = {}
for lp in logs:
    try:
        text = open(lp, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    for line in text.split("\n"):
        matched = False
        for fam, rx in FAMS.items():
            if rx.search(line):
                counts[fam] += 1
                if len(samples[fam]) < 2:
                    samples[fam].append(line.strip()[:180])
                matched = True
        if not matched and "<" in line and not KNOWN.search(line):
            m = re.search(r"<([A-Za-z][A-Za-z _:]{3,40})>", line)
            if m:
                tag = m.group(1)
                unknown[tag] = unknown.get(tag, 0) + 1

print("\n== TARGET FAMILIES ==")
for fam, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{c:>6}  {fam}")
    for s in samples[fam]:
        print("        ", s)

print("\n== TOP UNPARSED EVENT TAGS (new candidates) ==")
for tag, c in sorted(unknown.items(), key=lambda x: -x[1])[:22]:
    print(f"{c:>6}  <{tag}>")
