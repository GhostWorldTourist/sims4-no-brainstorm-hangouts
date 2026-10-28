"""No Brainstorm Hangouts - build script.

City Living's apartment neighbours drop by on a schedule. One of the visits they
can pick is a "brainstorm" hangout - the knock that puts "Invite to Brainstorm"
and "Reject Brainstorm" in the pie menu. The ordinary hangouts stay; only the
brainstorm ones go.

How this works
--------------
The apartment and penthouse zone directors keep a walkby schedule of weighted
situations. When it picks one, `_DesiredSituations.get_weighted_situations`
scores each entry as

    entry.weight * entry.weight_multipliers * entry.situation.weight_multipliers

so a situation can veto itself everywhere it is scheduled through its own
`weight_multipliers`. Its `base_value` is locked at 1, but the `multipliers`
list (TunableRange, minimum 0) is open, and an entry with no tests always
applies. This adds one `multiplier 0` entry to each of the six brainstorm
situations. They score zero, `weighted_random_item` never draws them, and the
neighbour picks another visit instead.

Overriding the six small situations rather than the zone directors keeps this
off the 50-80 KB director tuning that other mods are far more likely to touch.
No script, so nothing runs during play.

The XML is read from the installed game at build time and edited, so a rebuild
after a patch picks up whatever EA changed.

Author: GhostWorldTourist
"""
import os, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.environ['LOCALAPPDATA'], 'sulskill', 'ts4-knowledge', 'lib'))
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'repos', 'sulskill', 'sulskill-modbuild', 'scripts'))
import mergedtuning, dbpf

SOURCE = r'C:\Games\The Sims 4\Delta\EP03\SimulationDeltaBuild0.package'
T_SITUATION = 0xFBC3AEEB
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'GhostWorldTourist_NoBrainstormHangouts.package')

BRAINSTORM = {
    141316: 'situationComplex_NeighborHangout_Brainstorm_ArtLover',
    141317: 'situationComplex_NeighborHangout_Brainstorm_Creative',
    146268: 'situationComplex_NeighborHangoutPenthouse_Brainstorm_KeyHolders_ArtLover',
    146269: 'situationComplex_NeighborHangoutPenthouse_Brainstorm_KeyHolders_Creative',
    146270: 'situationComplex_NeighborHangoutPenthouse_Brainstorm_NonKeyHolders_ArtLover',
    146273: 'situationComplex_NeighborHangoutPenthouse_Brainstorm_NonKeyHolders_Creative',
}


def veto(elem):
    if elem.find("*[@n='weight_multipliers']") is not None:
        raise SystemExit('%s already tunes weight_multipliers; EA changed it, '
                         'review before rebuilding' % elem.get('n'))
    wm = ET.SubElement(elem, 'U', n='weight_multipliers')
    entry = ET.SubElement(ET.SubElement(wm, 'L', n='multipliers'), 'U')
    ET.SubElement(entry, 'T', n='multiplier').text = '0'
    elem[:] = sorted(elem, key=lambda e: e.get('n', ''))


def main():
    found = {}
    for _, _, ct in mergedtuning.iter_resources(SOURCE):
        for inst in ct.instances():
            if inst.res_type == 'situation' and int(inst.attrs['s']) in BRAINSTORM:
                found[int(inst.attrs['s'])] = ct.expand(inst)
    missing = set(BRAINSTORM) - set(found)
    if missing:
        print('NOT FOUND: %s' % sorted(missing), file=sys.stderr)
        return 2
    resources = []
    for iid in sorted(found):
        elem = found[iid]
        assert elem.get('n') == BRAINSTORM[iid], (iid, elem.get('n'))
        veto(elem)
        xml = b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(elem, encoding='utf-8')
        resources.append((T_SITUATION, 0, iid, xml))
        print('  %s' % BRAINSTORM[iid])
    n, size = dbpf.write(OUT, resources)
    print('\nwrote %s\n  %d resources, %d bytes' % (OUT, n, size))
    return 0


if __name__ == '__main__':
    sys.exit(main())
