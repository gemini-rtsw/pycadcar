from caproto.server import pvproperty, PVGroup
import caproto


from enum import IntEnum, Enum


# Apply and CAD VALs - other systems count - not sure if this is a problem
class Result(IntEnum):
    ERROR = 0
    SUCCESS = 1

class CARState:
    IDLE = "IDLE"
    PAUSED = "PAUSED"
    BUSY = "BUSY"
    ERR = "ERR"





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


class ApplyRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_records = []
        self.car_record = None


    def has_sub_records(self):
        return len(self.sub_records) > 0
    
    def has_car_record(self):
        return self.car_record != None
    
    async def update_car(self, car_state, message, clid):
        if (self.has_car_record()):
            print(f'Updating {self.car_record.prefix} VAL={car_state} CLID={clid} OMSS={message}')
            await self.car_record.VAL.write(car_state)
            await self.car_record.CLID.write(clid)
            await self.car_record.OMSS.write(message)



    # ------------------ DIR  ------------------------- 
    DIR = pvproperty(
        value='MARK',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['MARK', 'CLEAR', 'PRESET', 'START', 'STOP'],
        name="DIR"
    )

    @DIR.putter
    async def DIR(self, instance, value):
        await self.DIRputter(instance, value)

    async def DIRputter(self, instance, value):
        print(f"{self.prefix} Processing Sub Records: {[obj.__class__.__name__ for obj in self.sub_records]}")
        #Writing the START directive forces the PRESET directive to be sent to all links before the START directive is sent.
        if value == 'START':
            await self.setSubRecordDir('PRESET')

        await self.setSubRecordDir(value)
        return value
    




    async def setError(self, message):
        print(f"Setting {self.prefix}MESS = {message}")
        await self.MESS.write(message)
        await self.VAL.write(Result.ERROR)

        self.update_car(CARState.ERR, message, self.CLID.value)


    async def clearError(self, message = ''):
        print(f"Setting {self.prefix}MESS = none")
        await self.MESS.write('')
        await self.VAL.write(Result.SUCCESS)

        self.update_car(CARState.IDLE, message, self.CLID.value)


    async def setSuccess(self, message = "Directive State Success"):
        print(f"Setting {self.prefix}MESS = {message}")
        await self.MESS.write(message)
        await self.VAL.write(Result.SUCCESS)

        self.update_car(CARState.IDLE, message, self.CLID.value)


    async def setBusy(self, message = "Directive State Busy"):
        print(f"Setting {self.prefix}MESS = {message}")
        await self.MESS.write(message)
        await self.VAL.write(Result.SUCCESS)

        self.update_car(CARState.BUSY, message, self.CLID.value)

        # update CAR
#        if (self.has_car_record()  and not self.has_sub_records()):
#            print(f'Updating {self.car_record.prefix}VAL to BUSY')
#            await self.car_record.VAL.write(CARState.BUSY)
#            await self.car_record.CLID.write(self.VAL.value)            
            


    async def setSubRecordDir(self, value):

        # Set CAR record to BUSY
 #       if (self.car_record != None):
 #           print(f'Updating {self.car_record.prefix}VAL')
  #          await self.setBusy()


        await self.setBusy()


        #Set the DIR value for all cadRecord instances to match applyRecord's DIR
            
        processedCAD = False

        for sub_record in self.sub_records:
            print(f'{self.prefix} Processing {sub_record.prefix} ...')

            # a CAD record will process if MARKed or NOT in state 0
            if (sub_record.DIR.value == 'MARK' or sub_record.state_machine.state > 0):
                print(f"CAD {sub_record.prefix} will process")
                processedCAD = True

            await sub_record.DIR.write(value)

            # results
            ret_val  = sub_record.VAL.value
            ret_mess = sub_record.MESS.value

            print(f'{sub_record.prefix} VAL: {str(ret_val)}')

            if sub_record.VAL.value <= 0:
                print(f"Error processing cad record: {sub_record.prefix}")
                break  


#        # only set VAL and MESS if there is a CAD
#        if (len(self.sub_records) > 0):
#            print(f"VAL: {ret_val}")
#            print(f"MESS: {ret_mess}")
#            await self.VAL.write(ret_val)
#            await self.MESS.write(ret_mess)

#        if no CADs process we need to set the success manually
        if processedCAD == False:
            await self.setSuccess("Command Succeeded")



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

#        if (self.car_record != None):
#            print(f'Updating {self.car_record.prefix}CLID')
#            await self.car_record.CLID.write(value)

    # ------------------ MESS  ------------------------- 
    MESS = pvproperty(value='Initialized', dtype=caproto.ChannelType.STRING, name="MESS")
    @MESS.putter
    async def MESS(self, instance, value):
        await self.MESSputter(instance, value)

    async def MESSputter(self, instance, value):
        print(f'{self.prefix}MESS value changed to: {value}')












