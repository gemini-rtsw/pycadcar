from caproto.server import pvproperty, PVGroup
import caproto



from enum import IntEnum, Enum

import sys


#try import locally for testing
sys.path.insert(0, '../')
from pygeminirec.base import BaseExecutor
from pygeminirec.base import CADDirective
from pygeminirec.base import CARState
from pygeminirec.base import Result



    # This implements Java ACM code as of 2024 March
    #  
    # Gemini record reference manual implies 0 is success 
    # Gemini Record Ref - Apply.VAL - This is the return value from the input links. If any link returns a non-zero, processing stops and the last value is returned.
    # 
    # Java ACM README - 1. If any CAD record returns an error value, the apply record changes apply.VAL to an error value (negatives values are error codes) and puts the error message from the CAD record in apply.MESS.
    #
    # code says this: (VAL <= 0 is error)
    #       public State onApplyValChange(Integer val, Instant timestamp) {
    #            if(val > 0) {
    #                if(clid.isPresent()) return this;
    #                else {
    #                    boolean ended = carClid.map(y -> commandState.checkCompletion(timestamp, val, y, cm)).orElse(false);
    #                    if (ended) return IdleState;
    #                    else return new BusyState(cm, commandState, Optional.of(val), carClid);
    #                }
    #            } else {
    #                failCommandWithApplyError(cm);
    #                return IdleState;
    #            }
    #        }
    #
    #
    #
    # 1  Seqexec sets the file name and writes a START to apply.DIR
    # 2  apply.VAL changes value. apply.VAL > 0 is the CLID for the command. Otherwise is an error, and the error message can be read at apply.MESS
    # 3  applyC.CLID changes to the value of the CLID given by apply.VAL
    # 4  applyC.VAL changes to BUSY
    # 5  observeC.CLID changes to the value of the CLID given by apply.VAL
    # 6  observeC.VAL changes to BUSY
    # 7  applyC.VAL changes to IDLE
    # 8  After the exposure is completed and the file sent to DHS, observeC.VAL changes to IDLE. It can also change to PAUSED or ERROR. In the last case, the error message is read from observeC.OMSS
    #
    

#   Here's the operational GNIRS applyC and observeC during an observation:
#   nirs:dc:applyC.CLID            2022-11-22 10:45:14.330714 52
#   nirs:dc:observeC.CLID          2022-11-22 10:45:14.281047 52
#   nirs:dc:observeC               2022-11-22 10:45:14.281047 BUSY
#   nirs:dc:apply.CLID             2022-11-22 10:45:14.314158 52
#   nirs:dc:apply                  2022-11-22 10:45:14.314158 52
#   nirs:dc:applyC                 2022-11-22 10:45:14.330714 BUSY
#   nirs:dc:applyC.CLID            2022-11-22 10:45:15.340603 52
#   nirs:dc:applyC                 2022-11-22 10:45:15.340603 IDLE
#   nirs:dc:observeC.CLID          2022-11-22 10:45:16.536436 52
#   nirs:dc:observeC               2022-11-22 10:45:16.536436 IDLE
    
#   I modified the new DC to set applyC and observeC in the same order (it was doing it in a different order):
#   tgnirs:dc:apply.CLID           2022-11-22 16:17:01.644676 1
#   tgnirs:dc:observeC.CLID        2022-11-22 16:17:01.644708 1
#   tgnirs:dc:observeC             2022-11-22 16:17:01.644708 BUSY
#   tgnirs:dc:applyC.CLID          2022-11-22 16:17:01.644749 1
#   tgnirs:dc:applyC               2022-11-22 16:17:01.644749 BUSY
#   tgnirs:dc:applyC.CLID          2022-11-22 16:17:03.645020 1
#   tgnirs:dc:applyC               2022-11-22 16:17:03.645020 IDLE
#   tgnirs:dc:observeC.CLID        2022-11-22 16:17:04.645710 1
#   tgnirs:dc:observeC             2022-11-22 16:17:04.645710 IDLE

#   working sequence to set parameters with python ioc   
#   [software@hbftelops-ld3 ~]$ caput tgnirs:dc:applyC.CLID 1 && caput tgnirs:dc:applyC.VAL 2 && caput tgnirs:dc:applyC.VAL 0
#   Old : tgnirs:dc:applyC.CLID          0
#   New : tgnirs:dc:applyC.CLID          1
#   Old : tgnirs:dc:applyC.VAL           IDLE
#   New : tgnirs:dc:applyC.VAL           BUSY
#   Old : tgnirs:dc:applyC.VAL           BUSY
#   New : tgnirs:dc:applyC.VAL           IDLE
#   [software@hbftelops-ld3 ~]$


#[software@hbftelops-ld3 ~]$ caput tgnirs:dc:applyC.CLID 1 && caput tgnirs:dc:applyC.VAL 2 && caput tgnirs:dc:applyC.VAL 0
#Old : tgnirs:dc:applyC.CLID          1
#New : tgnirs:dc:applyC.CLID          1
#Old : tgnirs:dc:applyC.VAL           BUSY
#New : tgnirs:dc:applyC.VAL           BUSY
#Old : tgnirs:dc:applyC.VAL           BUSY
#New : tgnirs:dc:applyC.VAL           IDLE

#[software@hbftelops-ld3 ~]$ caput tgnirs:dc:apply.CLID 1 && caput tgnirs:dc:applyC.CLID 1 && caput tgnirs:dc:applyC.VAL IDLE && caput tgnirs:dc:applyC.VAL BUSY && caput tgnirs:dc:applyC.VAL IDLE
#Old : tgnirs:dc:apply.CLID           1
#New : tgnirs:dc:apply.CLID           1
#Old : tgnirs:dc:applyC.CLID          1
#New : tgnirs:dc:applyC.CLID          1
#Old : tgnirs:dc:applyC.VAL           IDLE
#New : tgnirs:dc:applyC.VAL           IDLE
#Old : tgnirs:dc:applyC.VAL           IDLE
#New : tgnirs:dc:applyC.VAL           BUSY
#Old : tgnirs:dc:applyC.VAL           BUSY
#New : tgnirs:dc:applyC.VAL           IDLE

################################
#
#[software@hbftelops-ld3 ~]$ caput tgnirs:dc:apply.CLID 1 && caput tgnirs:dc:applyC.CLID 1 && caput tgnirs:dc:observeC.CLID 1 && caput tgnirs:dc:applyC.VAL IDLE && caput tgnirs:dc:observeC.VAL IDLE && caput tgnirs:dc:observeC.VAL BUSY && caput tgnirs:dc:applyC.VAL BUSY && caput tgnirs:dc:applyC.VAL IDLE && caput tgnirs:dc:observeC.VAL IDLE
#Old : tgnirs:dc:apply.CLID           1
#New : tgnirs:dc:apply.CLID           1
#Old : tgnirs:dc:applyC.CLID          1
#New : tgnirs:dc:applyC.CLID          1
#Old : tgnirs:dc:observeC.CLID        1
#New : tgnirs:dc:observeC.CLID        1
#Old : tgnirs:dc:applyC.VAL           IDLE
#New : tgnirs:dc:applyC.VAL           IDLE
#Old : tgnirs:dc:observeC.VAL         IDLE
#New : tgnirs:dc:observeC.VAL         IDLE
#Old : tgnirs:dc:observeC.VAL         IDLE
#New : tgnirs:dc:observeC.VAL         BUSY
#Old : tgnirs:dc:applyC.VAL           IDLE
#New : tgnirs:dc:applyC.VAL           BUSY
#Old : tgnirs:dc:applyC.VAL           BUSY
#New : tgnirs:dc:applyC.VAL           IDLE
#Old : tgnirs:dc:observeC.VAL         BUSY
#New : tgnirs:dc:observeC.VAL         IDLE


#tgnirs:dc:apply.CLID           2024-03-21 09:04:31.493962 1  
#tgnirs:dc:apply.CLID           2024-03-21 09:04:34.557318 1  
#tgnirs:dc:applyC.VAL           2024-03-21 09:04:34.674262 IDLE  
#tgnirs:dc:observeC.VAL         2024-03-21 09:04:34.716088 IDLE  
#tgnirs:dc:observeC.VAL         2024-03-21 09:04:34.752762 BUSY  
#tgnirs:dc:applyC.VAL           2024-03-21 09:04:34.792297 BUSY  
#tgnirs:dc:applyC.VAL           2024-03-21 09:04:34.834194 IDLE  
#tgnirs:dc:observeC.VAL         2024-03-21 09:04:34.875928 IDLE




class ApplyRecord(PVGroup, BaseExecutor):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        PVGroup.__init__(self, *args, **kwargs)  # Explicitly call PVGroup's constructor
        BaseExecutor.__init__(self)  # Explicitly call BaseExecutor's constructor
    
    async def set_state(self, **kwargs):
        # state - Result.ERROR or Result.SUCCESS
        # message
        # clid
        print(f'Updating Sub {self.prefix} VAL={kwargs["state"]} CLID={kwargs["clid"]} MESS={kwargs["message"]}')
        await self.CLID.write(kwargs['clid'])
        await self.MESS.write(kwargs['message'])
        await self.VAL.write(kwargs['state'])  

        return Result.SUCCESS, kwargs['message']


    async def processDirective(self, value):
        print("-----------------------------------")
        print(f'{self.prefix} Processing Directive')

        # get the CLID and reset if it was set to error last directive
        clid = self.CLID.value
        if (clid < 0):
            clid = 0

        # increment CLID to start a new directive
        clid = clid + 1
        print("++++++++++++++++++++++++++++++++++++")
        print("Set CADs state")
        await self.update_all_cad_states(reverse = False, state = Result.SUCCESS, message = f"Processing Directive {self.prefix}DIR = {value}", clid = clid)


        print("Process Directive")
        ret, ret_mess, ret_cad = await self.process_all_cad_directives(reverse = False, directive = value)







    # ------------------ DIR  ------------------------- 
    DIR = pvproperty(
        value=CADDirective.PRESET,
        dtype=caproto.ChannelType.ENUM,
        enum_strings=[CADDirective.MARK, CADDirective.CLEAR, CADDirective.PRESET, CADDirective.START, CADDirective.STOP],
        name="DIR"
    )

    @DIR.putter
    async def DIR(self, instance, value):
        await self.DIRputter(instance, value)

    async def DIRputter(self, instance, value):
        print(f"{self.prefix} Processing Sub Records: {[obj.__class__.__name__ for obj in self.cads.records]}")

        await self.processDirective(value)
        return value
    



    # ------------------ VAL  ------------------------- 
    VAL = pvproperty(
        value=Result.SUCCESS,  # Assuming 0 as the default integer value
        dtype=caproto.ChannelType.LONG,
        name="VAL"
    )
    @VAL.putter
    async def VAL(self, instance, value):
        await self.VALputter(instance, value)

    async def VALputter(self, instance, value):
        print(f'{self.prefix}VAL value changed to: {value}')



    # ------------------ CLID  ------------------------- 
    CLID = pvproperty(value=0, dtype=caproto.ChannelType.LONG, name="CLID")
    @CLID.putter
    async def CLID(self, instance, value):
        await self.CLIDputter(instance, value)

    async def CLIDputter(self, instance, value):
        print(f'{self.prefix}CLID value changed to: {value}')


    # ------------------ MESS  ------------------------- 
    MESS = pvproperty(value='Initialized', dtype=caproto.ChannelType.STRING, name="MESS")
    @MESS.putter
    async def MESS(self, instance, value):
        await self.MESSputter(instance, value)

    async def MESSputter(self, instance, value):
        print(f'{self.prefix}MESS value changed to: {value}')












