rtRequest(Clk:=bRequest);
tDoorOpen(In:=bDoorLatch,PT:=T#5S);
tStop(In:=NOT Machine_Data.OUT.bRunning,PT:=T#0.5S);
IF rtRequest.Q AND Machine_Data.OUT.bRunning AND Machine_Data.IN.bDoorClosed AND NOT tDoorOpen.Q THEN
 bCanOpen:=TRUE;
ELSIF tDoorOpen.Q THEN
      bCanOpen:=FALSE;
END_IF;
bDoorLock:=bCanOpen OR tStop.Q;
bRequestLight:=bDoorLock;