using System;
using System.Collections.Generic;
using System.Linq;
using DBDef;
using Thea2.Common;
using Thea2.Server;
using Group = Thea2.Server.Group;

namespace GameScript
{
    // Experimental staged assembly: crafted body + crafted elemental core => living recruit.
    // Separate from the existing unique Guardian / Reliquia / Komainu awakenings.
    public class YM_GolemAssembly : ScriptBase
    {
        private static readonly Dictionary<string, string> Tiers = new Dictionary<string, string>
        {
            { "CHOQUE", "T1" }, { "CASCALHO", "T1" }, { "GALHO", "T1" },
            { "LAMPEJO", "T1" }, { "MASSA", "T1" }, { "SEIXO", "T1" },
            { "FERRO_VIDO", "T2" }, { "RAIZ", "T2" }, { "OSSADA", "T2" },
            { "CRISTAL", "T2" }, { "PAO_DO_CAMPO", "T2" },
            { "MURALHA", "T3" }, { "VIUVA", "T3" }, { "VEJO", "T3" },
            { "AGULHA", "T3" }, { "FERREIRO", "T3" },
            { "OBSIDIANA", "T3" }, { "SANGUE", "T3" },
            { "NEBULINA", "T3" }, { "FUNGO", "T3" }
        };

        private static Group OwnGroup(AdventureEventData data)
        {
            if (data == null) return null;
            var group = data.GetMainPlayerGroup();
            return group != null && !group.abstractGroup &&
                group.ownerID == data.GetMainPlayerID() ? group : null;
        }

        private static bool HasYuri(Group group)
        {
            return group != null && group.GetCharactersAsList().Any(character =>
                character != null && character.subrace.Get() != null &&
                character.subrace.Get().dbName == "SUBRACE-YURI_MIZUKI");
        }

        private static string KeyOf(string subraceId)
        {
            const string prefix = "SUBRACE-GOLEM_";
            if (string.IsNullOrEmpty(subraceId) || !subraceId.StartsWith(prefix, StringComparison.Ordinal))
                return null;
            var key = subraceId.Substring(prefix.Length);
            return Tiers.ContainsKey(key) ? key : null;
        }

        private static ItemBase FindPart(Group group, string tagId)
        {
            if (group == null || group.items == null) return null;
            var tag = Globals.GetInstanceFromDB<Tag>(tagId);
            if (tag == null) return null;
            var entry = group.items.FirstOrDefault(stack =>
                stack.GetItem() != null && stack.GetItem().attributes.Contains(tag, FInt.ONE));
            return entry != null ? entry.GetItem() : null;
        }

        private static bool CanAssemble(Group group, string subraceId)
        {
            string key = KeyOf(subraceId);
            if (key == null || !HasYuri(group) ||
                Globals.GetInstanceFromDB<Subrace>(subraceId) == null)
                return false;
            return FindPart(group, "TAG-YM_BODY_" + key) != null &&
                FindPart(group, "TAG-YM_CORE_" + Tiers[key]) != null;
        }

        [ScriptAttribute(typeof(Subrace))]
        public static bool FRA_YM_HasAssemblyParts(AdventureEventData data,
            LogicResultAction action, AdvNode node)
        {
            return CanAssemble(OwnGroup(data), action.scriptCallWithTag.tag);
        }

        private static void ReportConsumed(AdventureEventData data, ItemBase item, Group group)
        {
            var change = new AdventureEventDataChange();
            change.GatherReferenceInfo(item);
            change.count = -1;
            change.playerID = group.ownerID;
            data.AddUncollectedAdventureChange(change);
        }

        [ScriptAttribute(typeof(Subrace))]
        public static void FMO_YM_CompleteAssembly(NOAdventureStatus status,
            AdventureEventData data, LogicModifier modifier, AdvNode node)
        {
            var group = OwnGroup(data);
            var subraceId = modifier.scriptCallWithTag.tag;
            var game = GameInstance.Get();
            if (game == null || !CanAssemble(group, subraceId)) return;

            lock (game)
            {
                // Re-check inside lock so an item cannot be consumed twice.
                if (!CanAssemble(group, subraceId)) return;
                string key = KeyOf(subraceId);
                ItemBase body = FindPart(group, "TAG-YM_BODY_" + key);
                ItemBase core = FindPart(group, "TAG-YM_CORE_" + Tiers[key]);
                var form = Globals.GetInstanceFromDB<Subrace>(subraceId);
                if (body == null || core == null || form == null) return;

                var bodyTaken = group.TakeItem(body, 1);
                if (bodyTaken == null || bodyTaken.GetItem() == null) return;

                var coreTaken = group.TakeItem(core, 1);
                if (coreTaken == null || coreTaken.GetItem() == null)
                {
                    group.AddItem(bodyTaken);
                    return;
                }

                Character awakened;
                try
                {
                    awakened = Character.Instantiate(group, form, 1, false);
                }
                catch
                {
                    group.AddItem(bodyTaken);
                    group.AddItem(coreTaken);
                    throw;
                }

                if (awakened == null)
                {
                    group.AddItem(bodyTaken);
                    group.AddItem(coreTaken);
                    return;
                }

                // Consume only after successful character creation.
                ReportConsumed(data, bodyTaken.GetItem(), group);
                ReportConsumed(data, coreTaken.GetItem(), group);
                bodyTaken.GetItem().Destroy();
                coreTaken.GetItem().Destroy();

                var reward = new AdventureEventDataChange();
                reward.GatherReferenceInfo(awakened);
                reward.count = 1;
                reward.playerID = group.ownerID;
                data.AddUncollectedAdventureChange(reward);
            }
        }
    }
}
