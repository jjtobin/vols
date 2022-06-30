context = h_init()
context.set_state('ProjectSummary', 'proposal_code', 'VLA/22A-195')
context.set_state('ProjectSummary', 'proposal_title', 'VOLS')
context.set_state('ProjectSummary', 'piname', 'Gemma Busquet')
context.set_state('ProjectSummary', 'observatory', 'Karl G. Jansky Very Large Array')
context.set_state('ProjectSummary', 'telescope', 'EVLA')
import numpy as np

def detect_and_order_spws(msfile):
   tb.open(msfile+'/SPECTRAL_WINDOW')
   names=tb.getcol('NAME')
   freqs=tb.getcol('REF_FREQUENCY')
   nchan=tb.getcol('NUM_CHAN')
   bw=tb.getcol('TOTAL_BANDWIDTH')
   tb.close()

   cont_spwlist_no_order=''
   for i in range(len(names)):
      if 'EVLA_C' in names[i]:
         if nchan[i] == 64:
            cont_spwlist_no_order+=str(i)+','
   cont_spwlist_no_order=cont_spwlist_no_order[:-1]
   freq_sort_order=np.argsort(freqs)
   freqs=freqs[freq_sort_order]
   names=names[freq_sort_order]
   nchan=nchan[freq_sort_order]
   bw=bw[freq_sort_order]
   chanwidth=bw/nchan
   print(freq_sort_order)
   spwlist=''
   cont_spwlist=''
   line_spwlist=''
   for i in range(len(freq_sort_order)):
      if 'EVLA_C' in names[i]:
         spwlist+=str(freq_sort_order[i])+','
         if nchan[i] == 64:
            cont_spwlist+=str(freq_sort_order[i])+','
         else:
            line_spwlist+=str(freq_sort_order[i])+','
   cont_spwlist=cont_spwlist[:-1]
   line_spwlist=line_spwlist[:-1]
   print(spwlist)
   return cont_spwlist,line_spwlist,cont_spwlist_no_order
    
      

import os
import glob
vislist=glob.glob('../rawdata/22A-195*')
msfile=vislist[0].split('/')[2]+'.ms'
#if not os.path.exists(vislist[0]+'/Scan.xml.backup'):  # if backup file exists, assume we've already edited the intents
#   os.system('cp '+vislist[0]+'/Scan.xml '+vislist[0]+'/Scan.xml.backup')
#   os.system('sed -i "s/1 1 CALIBRATE_BANDPASS/1 2 CALIBRATE_BANDPASS CALIBRATE_POL_LEAKAGE/g" '+vislist[0]+'/Scan.xml')


try:
    hifv_importdata(vis=vislist, session=['session_1'])

    #hifv_hanning(pipelinemode="automatic")
    #only hanning smooth the continuum data
    #get spws in frequency order and separated between line and continuum
    cont_spwlist,line_spwlist,cont_spwlist_no_order=detect_and_order_spws(msfile)

    ms.open(msfile,nomodify=False)
    staql={'spw':cont_spwlist_no_order}
    ms.msselect(staql)
    ms.hanningsmooth('data')
    ms.close()

    hifv_flagdata(hm_tbuff='1.5int', fracspw=0.01, intents='*POINTING*,*FOCUS*,*ATMOSPHERE*,*SIDEBAND_RATIO*, *UNKNOWN*, *SYSTEM_CONFIGURATION*, *UNSPECIFIED#UNSPECIFIED*')
    hifv_vlasetjy(pipelinemode="automatic")
    hifv_priorcals(pipelinemode="automatic")
    hifv_syspower(apply=True,clip_sp_template=[0.75, 1.2])
    hifv_testBPdcals(pipelinemode="automatic")
    hifv_checkflag(checkflagmode='bpd-vla')
    hifv_semiFinalBPdcals(pipelinemode="automatic")
    hifv_checkflag(checkflagmode='allcals-vla')
    hifv_solint(pipelinemode="automatic")
    hifv_fluxboot(pipelinemode="automatic")
    hifv_finalcals(pipelinemode="automatic")
    hifv_circfeedpolcal(pipelinemode="automatic")
    hifv_applycals(pipelinemode="automatic")
    hifv_checkflag(checkflagmode='target-vla')
    hifv_targetflag(intents='*TARGET*')
    hifv_statwt(pipelinemode="automatic")
    hifv_plotsummary(pipelinemode="automatic")
    hif_makeimlist(intent='PHASE,BANDPASS', specmode='cont')
    hif_makeimages(hm_masking='centralregion')
    hifv_exportdata(pipelinemode="automatic")
    #split continuum MS in frequency order
    mstransform(vis=msfile,
            outputvis=msfile.replace('.ms','_cont.ms'),
            spw=cont_spwlist,
            intent='OBSERVE_TARGET#UNSPECIFIED', datacolumn='corrected',
            chanaverage=False, chanbin=1, timeaverage=True, timebin='8s',
            reindex=True)


    mstransform(vis=msfile,
            outputvis=msfile.replace('.ms','_line_with_rfi_flags.ms'),
            spw=line_spwlist,
            intent='OBSERVE_TARGET#UNSPECIFIED', datacolumn='corrected',
            chanaverage=False, chanbin=1, timeaverage=True, timebin='8s',
            reindex=True)

    #get flag versions to figure out which one was before statwt
    flagversions=flagmanager(vis=msfile,mode='list')
    versionname=''
    for i in flagversions.keys(): 
       if 'hifv_checkflag_target-vla' in flagversions[i]['name']:
          print(flagversions[i]['name'])
          versionname=flagversions[i]['name']
          break   # break put in to avoid running into a python error 

    #put flagging state to before selfcal
    flagmanager(mode='restore',vis=msfile,versionname=versionname)

    #split off non non-RFI flagged data to line.ms
    mstransform(vis=msfile,
            outputvis=msfile.replace('.ms','_line.ms'),
            spw=line_spwlist,
            intent='OBSERVE_TARGET#UNSPECIFIED', datacolumn='corrected',
            chanaverage=False, chanbin=1, timeaverage=True, timebin='8s',
            reindex=True)
    line_vis=msfile.replace('.ms','_line.ms')
    flagmanager(mode='save',vis=line_vis,versionname='before_rflag_statwt')

    #put flags back in
    flagmanager(mode='restore',vis=msfile,versionname='Pipeline_Final')

finally:
    h_save()



