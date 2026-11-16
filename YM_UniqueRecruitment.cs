using DBDef;
using Thea2.Common;
using Thea2.Server;
using UnityEngine;

namespace GameScript
{
    public class YM_UniqueRecruitment : ScriptBase
    {
        private const string CharacterId = "SUBRACE-YURI_MIZUKI";
        private const string RecruitedId = "TAG-YM_UNIQUE_RECRUITED";

        [ScriptAttribute(null)]
        public static void FMO_YM_DiscoverResearch(NOAdventureStatus status, AdventureEventData data,
            LogicModifier modifier, AdvNode node)
        {
            var game = GameInstance.Get();
            var group = data.GetMainPlayerGroup();
            var discovery = Globals.GetInstanceFromDB<Tag>("TAG-YM_TECH_DISCOVERED");
            if (game == null || group == null || group.abstractGroup || discovery == null ||
                group.ownerID != data.GetMainPlayerID())
                return;

            game.sharedAttributes.SetBaseTo(discovery, FInt.ONE);
            foreach (var member in group.GetCharactersAsList())
                if (member != null)
                    member.attributes.SetBaseTo(discovery, FInt.ONE);
        }

        [ScriptAttribute(null)]
        public static bool FRA_YM_UniqueRecruitment(AdventureEventData data, LogicResultAction action, AdvNode node)
        {
            var game = GameInstance.Get();
            return IsAvailable(game) &&
                Random.Range(0, 100) < 25;
        }

        [ScriptAttribute(null)]
        public static void FMO_YM_UniqueRecruitment(NOAdventureStatus status, AdventureEventData data,
            LogicModifier modifier, AdvNode node)
        {
            var game = GameInstance.Get();
            lock (game)
            {
                var group = data.GetMainPlayerGroup();
                if (group == null || group.abstractGroup || !IsAvailable(game))
                    return;

                var subrace = Globals.GetInstanceFromDB<Subrace>(CharacterId);
                var character = Character.Instantiate(group, subrace, 1, true);
                if (character == null)
                    return;

                game.sharedAttributes.SetBaseTo(Globals.GetInstanceFromDB<Tag>(RecruitedId), FInt.ONE);
                var change = new AdventureEventDataChange();
                change.GatherReferenceInfo(character);
                change.count = 1;
                change.playerID = group.ownerID;
                data.AddUncollectedAdventureChange(change);

                foreach (var cargoId in new[] { "ITEM_CARGO-FEW_IRON", "ITEM_CARGO-ONE_AMBER", "ITEM_CARGO-ONE_LEATHER" })
                {
                    var cargo = Globals.GetInstanceFromDB<ItemCargo>(cargoId);
                    if (cargo == null)
                        continue;

                    var reward = ItemBase.InstantaiteFromToGroup(cargo, group, 1f, 1);
                    if (reward != null)
                        data.AddUncollectedAdventureChange(reward);
                }
            }
        }

        private static bool IsAvailable(GameInstance game)
        {
            var marker = Globals.GetInstanceFromDB<Tag>(RecruitedId);
            var subrace = Globals.GetInstanceFromDB<Subrace>(CharacterId);
            if (marker == null || subrace == null || game.sharedAttributes.Contains(marker, FInt.ONE))
                return false;

            foreach (var group in game.GetPlayerGroups())
            {
                foreach (var reference in group.characters)
                {
                    var character = reference.Get();
                    if (character != null && character.subrace.Get() == subrace)
                        return false;
                }
            }

            return true;
        }
    }
}
