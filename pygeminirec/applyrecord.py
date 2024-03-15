from caproto.server import pvproperty, PVGroup
import caproto


from enum import IntEnum

class Result(IntEnum):
    ERROR = 0
    SUCCESS = 1

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
    
class ApplyRecord(PVGroup):
    """Example group of PVs, where the prefix is defined on instantiation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_records = []


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

    async def clearError(self):
        print(f"Setting {self.prefix}MESS = {message}")
        await self.MESS.write('')
        await self.VAL.write(Result.SUCCESS)

    async def setSuccess(self, message):
        print(f"Setting {self.prefix}MESS = {message}")
        await self.MESS.write(message)
        await self.VAL.write(Result.SUCCESS)

    async def setSubRecordDir(self, value):

        """Set the DIR value for all cadRecord instances to match applyRecord's DIR."""

        for sub_record in self.sub_records:
            print(f'{self.prefix} Processing {sub_record.prefix} ...')

            await sub_record.DIR.write(value)

            # results
            ret_val  = sub_record.VAL.value
            ret_mess = sub_record.MESS.value

            print(f'{sub_record.prefix} VAL: {str(ret_val)}')

            if sub_record.VAL.value <= 0:
                print(f"Error processing cad record: {sub_record.prefix}")
                break  

        # only set VAL and MESS if there was a return from a sub record
        if (len(self.sub_records) > 0):
            print(f"VAL: {ret_val}")
            print(f"MESS: {ret_mess}")
            await self.VAL.write(ret_val)
            await self.MESS.write(ret_mess)


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












