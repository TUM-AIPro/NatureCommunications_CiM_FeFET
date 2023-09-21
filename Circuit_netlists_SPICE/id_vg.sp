*** 4 stages of FeFET ****


simulator lang=spice

.hdl "code/ferrocap.va"
.hdl "code/bsimimg.va"
.include "code/modelcard.nmos"

.param wv =0
.param vdd=0.7
.param tem=27
.temp=tem

    * --- Voltage Sources ---
    vdd supply  0 PWL(0 0, 20u 0, 20.001u 1, 35u 1)
    vfg fg 0 PWL(0 -4, 5u -4, 5.001u 0, 6u 0, 8u 0, 8.001u 0, 10u 0, 10.001u wv, 12u wv, 12.001u 0, 20u 0, 20.001u 0, 30u 0, 30.001u 0, 32u 2  )


    .model fecap pfecap 
simulator lang=spectre 
parameters del_vth=0
statistics {
process { 
vary del_vth dist=gauss std=0.040 percent=no
}
truncate tr=3.0
}
simulator lang=spice

   * --- FE-FDSOI Subcircuit ---
    .subckt nfefdsoi dr ga so bo
    Xnmos dr inga so bo aux nmos1 W=100n L=100n DELVTRAND=del_vth
    Xfe   ga inga aux fecap time_step=10n dir_init=1 Vo=5 m=3
    .ends
X1 int fg 0 0 nfefdsoi
r1 supply int r=10000k
*c1 sl 0 c=64f
simulator lang=spectre

simulatorOptions options reltol=1e-6 vabstol=1e-6 iabstol=1e-6 tnom=27 scalem=1.0 scale=1.0 gmin=1e-10 rforce=1 maxnotes=5 maxwarns=5 digits=0 cols=80 pivrel=1e-2 cmin=0.0001f

//uncomment for variability the next lines and the bracket

//MC montecarlo variations=process seed=1234 numruns=100
//{
sw1 sweep param=wv values=[1, 2.5, 3.8, 5.5] // Please note the wv values are not the real write-voltages. These are the values selected to mimic experimentally observed characteristics
{
tranRun tran stop=32u outputstart=30.001u minstep=0.00000000000001p maxstep=0.1u writefinal="spectre.fc" annotate=status maxiters=100 autostop=no method=euler
//}
}

modelParameter info what=models where=rawfile
element info what=inst where=rawfile
outputParameter info what=output where=rawfile
//designParamVals info what=parameters where=rawfile
//primitives info what=primitives where=rawfile
subckts info what=subckts  where=rawfile
simulator lang=spice
.probe tran par'-i(vdd)'
.probe tran par'v(fg)'
.measure vth find v(fg) when i(vdd)=-100n from 30.001u
