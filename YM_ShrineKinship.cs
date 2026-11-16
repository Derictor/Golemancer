using System;
using System.Collections.Generic;
using System.Linq;
using DBDef;
using Thea2.Common;
using Thea2.General;
using Thea2.Server;
using Group = Thea2.Server.Group;

namespace GameScript
{
    public class YM_ShrineKinship : ScriptBase
    {
        private const string ChildPrefix = "SUBRACE-YM_DESC_";
        private const string HeritagePrefix = "SKILL-YM_LINHAGEM_";
        private static readonly string[] Origins = { "HUMAN", "ELF", "ORC", "DWARF", "GOBLIN", "SHADOWELF", "DEMON", "BEAST" };
        private static readonly string[] Guardians = { "GUARDAO_DA_MINA", "RELIQUIA", "KOMAINU" };

        private static Group OwnGroup(AdventureEventData data)
        {
            var group = data.GetMainPlayerGroup();
            return group != null && !group.abstractGroup && group.ownerID == data.GetMainPlayerID() ? group : null;
        }

        private static IEnumerable<Character> Members(Group group)
        {
            return group.characters.Select(reference => reference.Get()).Where(c => c != null);
        }

        private static bool HasTag(Character character, TAG tag)
        {
            return character.attributes.Contains((Tag)tag, FInt.ONE);
        }

        private static bool IsAdult(Character character)
        {
            return !HasTag(character, TAG.CHILD) && !HasTag(character, TAG.GROWING_UP);
        }

        private static bool HasMentor(Group group)
        {
            return Members(group).Any(c => c.subrace.Get().dbName == "SUBRACE-YURI_MIZUKI");
        }

        private static string GuardianKey(string id)
        {
            return Guardians.FirstOrDefault(key => id == "SUBRACE-GOLEM_" + key);
        }

        [ScriptAttribute(typeof(Subrace))]
        public static bool FRA_YM_CanAwakenGuard(AdventureEventData data, LogicResultAction action, AdvNode node)
        {
            var group = OwnGroup(data);
            string key = GuardianKey(action.scriptCallWithTag.tag);
            if (group == null || key == null || !HasMentor(group))
                return false;

            var tag = Globals.GetInstanceFromDB<Tag>("TAG-YM_CORE_" + key);
            return tag != null && group.items != null && group.items.Any(item =>
                item.GetItem() != null && item.GetItem().attributes.Contains(tag, FInt.ONE));
        }

        private static void Report(AdventureEventData data, Character character, Group group)
        {
            var change = new AdventureEventDataChange();
            change.GatherReferenceInfo(character);
            change.count = 1;
            change.playerID = group.ownerID;
            data.AddUncollectedAdventureChange(change);
        }

        [ScriptAttribute(typeof(Subrace))]
        public static void FMO_YM_AwakenGuard(NOAdventureStatus status, AdventureEventData data, LogicModifier modifier, AdvNode node)
        {
            var group = OwnGroup(data);
            string id = modifier.scriptCallWithTag.tag;
            string key = GuardianKey(id);
            if (group == null || key == null)
                return;

            lock (GameInstance.Get())
            {
                var form = Globals.GetInstanceFromDB<Subrace>(id);
                var tag = Globals.GetInstanceFromDB<Tag>("TAG-YM_CORE_" + key);
                if (form == null || tag == null || !HasMentor(group) || group.items == null)
                    return;
                var core = group.items.FirstOrDefault(stack =>
                    stack.GetItem() != null && stack.GetItem().attributes.Contains(tag, FInt.ONE));
                if (core == null)
                    return;

                var item = group.TakeItem(core.GetItem(), 1);
                if (item == null || item.GetItem() == null)
                    return;

                Character companion;
                try
                {
                    companion = Character.Instantiate(group, form, 1, false);
                }
                catch
                {
                    group.AddItem(item);
                    throw;
                }
                if (companion == null)
                {
                    group.AddItem(item);
                    return;
                }

                var spent = new AdventureEventDataChange();
                spent.GatherReferenceInfo(item.GetItem());
                spent.count = -1;
                spent.playerID = group.ownerID;
                data.AddUncollectedAdventureChange(spent);
                item.GetItem().Destroy();
                Report(data, companion, group);
            }
        }

        private static string IdentityOrigin(Character character)
        {
            var form = character.subrace.Get();
            string id = form.dbName;
            if (id == "SUBRACE-ELF_SHADOW" || id == "SUBRACE-ELDER_ELF_SHADOW" || id == "SUBRACE-LIGHT_SICK_ELF_SHADOW")
                return "SHADOWELF";
            if (id.StartsWith(ChildPrefix, StringComparison.Ordinal))
            {
                string origin = id.Substring(ChildPrefix.Length).Split('_')[0];
                if (Origins.Contains(origin))
                    return origin;
            }
            const string FantasticHybridPrefix = "SUBRACE-FCP_HALF_";
            const string FantasticMixedPrefix = "SUBRACE-FCP_MIXED_";
            foreach (string prefix in new[] { FantasticHybridPrefix, FantasticMixedPrefix })
            {
                if (!id.StartsWith(prefix, StringComparison.Ordinal))
                    continue;
                string origin = id.Substring(prefix.Length).Split('_')[0];
                if (Origins.Contains(origin))
                    return origin;
            }
            string ancestry = form.race.dbName.Substring("RACE-".Length);
            if (ancestry == "PIRATES") return "ORC";
            if (ancestry == "GNOLL") return "BEAST";
            return Origins.Contains(ancestry) ? ancestry : null;
        }

        private static bool IsGuardianKin(Character character)
        {
            string race = character.subrace.Get().race.dbName;
            return race == "RACE-YM_GOLEM" || race == "RACE-YM_MEIO_GOLEM";
        }

        private static IEnumerable<string> Heritages(Character character)
        {
            if (IsGuardianKin(character))
                yield return "GOLEM";
            string origin = IdentityOrigin(character);
            if (origin != null)
                yield return origin;
            if (character.learnedSkills == null)
                yield break;

            foreach (var instance in character.learnedSkills)
            {
                var source = instance.source.Get();
                if (source == null)
                    continue;
                string id = source.dbName;
                string[] prefixes = { HeritagePrefix, "SKILL-FCP_HERITAGE_" };
                foreach (string prefix in prefixes)
                {
                    if (!id.StartsWith(prefix, StringComparison.Ordinal))
                        continue;
                    string value = id.Substring(prefix.Length);
                    if (Origins.Contains(value))
                        yield return value;
                }
                if (HasTag(character, TAG.HALF_RACE))
                {
                    switch (id)
                    {
                        case "SKILL-RACE_ORCS": case "SKILL-RACE_PIRATE_ORCS": yield return "ORC"; break;
                        case "SKILL-RACE_ELVES": yield return "ELF"; break;
                        case "SKILL-RACE_DWARVES": yield return "DWARF"; break;
                        case "SKILL-RACE_GOBLINS": yield return "GOBLIN"; break;
                    }
                }
            }
        }

        private static IEnumerable<Character[]> Pairs(Group group)
        {
            var characters = Members(group).ToList();
            if (characters.Count(c => HasTag(c, TAG.CHILD)) >= 2)
                yield break;

            var adults = characters.Where(IsAdult).ToList();
            for (int i = 0; i < adults.Count; i++)
            {
                for (int j = i + 1; j < adults.Count; j++)
                {
                    var a = adults[i];
                    var b = adults[j];
                    bool aKin = IsGuardianKin(a);
                    bool bKin = IsGuardianKin(b);
                    if ((aKin && (bKin || IdentityOrigin(b) != null)) || (bKin && IdentityOrigin(a) != null))
                        yield return new[] { a, b };
                }
            }
        }

        [ScriptAttribute(null)]
        public static bool FRA_YM_CanHaveKin(AdventureEventData data, LogicResultAction action, AdvNode node)
        {
            var group = OwnGroup(data);
            return group != null && Pairs(group).Any();
        }

        [ScriptAttribute(null)]
        public static void FMO_YM_AddKin(NOAdventureStatus status, AdventureEventData data, LogicModifier modifier, AdvNode node)
        {
            var group = OwnGroup(data);
            if (group == null)
                return;
            lock (GameInstance.Get())
            {
                var pairs = Pairs(group).ToList();
                if (pairs.Count == 0)
                    return;
                var pair = pairs[UnityEngine.Random.Range(0, pairs.Count)];
                var traits = new HashSet<string>(Heritages(pair[0]));
                traits.UnionWith(Heritages(pair[1]));
                var visible = IdentityOrigin(pair[0]) ?? IdentityOrigin(pair[1]) ?? Origins.FirstOrDefault(traits.Contains) ?? "GOLEM";
                var form = Globals.GetInstanceFromDB<Subrace>(ChildPrefix + visible + "_CHILD");
                if (form == null)
                    return;
                var child = Character.Instantiate(group, form, 1, false);
                if (child == null)
                    return;
                foreach (var trait in traits.OrderBy(value => value, StringComparer.Ordinal))
                {
                    var skill = Globals.GetInstanceFromDB<Skill>(HeritagePrefix + trait);
                    if (skill != null)
                        child.LearnSkill(Character.SkillCategory.Personal, skill, FInt.ONE);
                }
                Report(data, child, group);
            }
        }

        private static IEnumerable<Character> GrowingKin(Group group)
        {
            return Members(group).Where(c => HasTag(c, TAG.GROWING_UP) &&
                c.subrace.Get().dbName.StartsWith(ChildPrefix, StringComparison.Ordinal) &&
                c.subrace.Get().dbName.EndsWith("_CHILD", StringComparison.Ordinal));
        }

        [ScriptAttribute(null)]
        public static bool FRA_YM_HasGrowingKin(AdventureEventData data, LogicResultAction action, AdvNode node)
        {
            var group = OwnGroup(data);
            return group != null && GrowingKin(group).Any();
        }

        [ScriptAttribute(null)]
        public static void FMO_YM_GrowKin(NOAdventureStatus status, AdventureEventData data, LogicModifier modifier, AdvNode node)
        {
            var group = OwnGroup(data);
            if (group == null)
                return;
            foreach (var child in GrowingKin(group).ToList())
            {
                var id = child.subrace.Get().dbName;
                var form = Globals.GetInstanceFromDB<Subrace>(id.Substring(0, id.Length - 6) + "_ADULT");
                if (form == null)
                    continue;
                var traits = Heritages(child).Distinct().ToList();
                child.attributes.SetBaseTo((Tag)TAG.GROWING_UP, FInt.ZERO);
                child.UpgradeSubraceTo(form, true, false);
                foreach (string trait in traits)
                {
                    var skill = Globals.GetInstanceFromDB<Skill>(HeritagePrefix + trait);
                    if (skill != null && (child.learnedSkills == null || !child.learnedSkills.Any(instance => instance.source.Get() == skill)))
                        child.LearnSkill(Character.SkillCategory.Personal, skill, FInt.ONE);
                }
                Report(data, child, group);
            }
        }
    }
}
