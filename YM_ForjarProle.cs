using DBDef;
using Thea2.Common;
using Thea2.Server;
using UnityEngine;

namespace GameScript
{
    public class YM_ForjarProle : ScriptBase
    {
        private const string PendingId = "TAG-YM_FORJAR_PROLE";
        private const string MarkerId = "TAG-YM_GOLEM_CHILD";
        private const string GrowingUpId = "TAG-GROWING_UP";

        [ScriptAttribute(null)]
        public static bool FRA_YM_ForjarProleReady(AdventureEventData data, LogicResultAction action, AdvNode node)
        {
            var player = GameInstance.Get().GetPlayer(data.GetMainPlayerID());
            var group = data.GetMainPlayerGroup();
            var deadlineTag = Globals.GetInstanceFromDB<Tag>("TAG-YM_FORJAR_DEADLINE");
            if (player == null || group == null || deadlineTag == null)
                return false;

            float deadline = player.attributes.GetBase(deadlineTag).ToFloat();
            if (deadline == 0)
                deadline = GameInstance.Get().sharedAttributes.GetBase(deadlineTag).ToFloat();
            return ServerManager.GetTurnManager().tunrIndex >= deadline;
        }

        [ScriptAttribute(null)]
        public static void FMO_YM_ForjarProle(NOAdventureStatus status, AdventureEventData data,
            LogicModifier modifier, AdvNode node)
        {
            var game = GameInstance.Get();
            var group = data.GetMainPlayerGroup();
            var list = data.GetList(modifier.list, node);
            var pending = Globals.GetInstanceFromDB<Tag>(PendingId);
            var marker = Globals.GetInstanceFromDB<Tag>(MarkerId);
            if (game == null || group == null || group.abstractGroup || list == null ||
                pending == null || marker == null)
                return;

            foreach (var key in list.GetList())
            {
                var character = list.GetItem(key).item as Character;
                if (character == null || character.group.Get() != group ||
                    character.attributes.Contains(pending, FInt.ONE))
                    continue;

                character.attributes.SetBaseTo(pending, FInt.ONE);
                var player = GameInstance.Get().GetPlayer(data.GetMainPlayerID());
                var deadlineTag = Globals.GetInstanceFromDB<Tag>("TAG-YM_FORJAR_DEADLINE");
                player.attributes.SetBaseTo(deadlineTag, (float)ServerManager.GetTurnManager().tunrIndex + 5);

                var change = new AdventureEventDataChange();
                change.GatherReferenceInfo(character);
                change.playerID = group.ownerID;
                data.AddUncollectedAdventureChange(change);
                return;
            }
        }

        [ScriptAttribute(typeof(Subrace))]
        public static void FMO_YM_FinishForjarProle(NOAdventureStatus status, AdventureEventData data,
            LogicModifier modifier, AdvNode node)
        {
            var group = data.GetMainPlayerGroup();
            var list = data.GetList(modifier.list, node);
            var form = Globals.GetInstanceFromDB<Subrace>(modifier.scriptCallWithTag.tag);
            var pending = Globals.GetInstanceFromDB<Tag>(PendingId);
            var marker = Globals.GetInstanceFromDB<Tag>(MarkerId);
            var growingUp = Globals.GetInstanceFromDB<Tag>(GrowingUpId);
            if (group == null || group.abstractGroup || list == null || form == null ||
                pending == null || marker == null || growingUp == null)
                return;

            foreach (var key in list.GetList())
            {
                var character = list.GetItem(key).item as Character;
                if (character == null || character.group.Get() != group ||
                    !character.attributes.Contains(pending, FInt.ONE))
                    continue;

                character.attributes.SetBaseTo(growingUp, FInt.ZERO);
                character.attributes.SetBaseTo(marker, FInt.ONE);
                character.UpgradeSubraceTo(form, true, false);
                character.attributes.SetBaseTo(pending, FInt.ZERO);

                var change = new AdventureEventDataChange();
                change.GatherReferenceInfo(character);
                change.count = 1;
                change.playerID = group.ownerID;
                data.AddUncollectedAdventureChange(change);
            }
        }
    }
}
