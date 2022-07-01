vislist=['22A-195.sb41668223.eb41788343.59699.900189837965_cont.ms']

image_data={'fieldlists': {'top': 'P98,P77,P56,P35,P112,P99,P78,P57,P36,P15,P37,P16,P17,P38,P59,P80,P101,P102,P81,P113,P100,P79,P58,P60,P39,P18,P19,P40,P61,P82,P103,P104,P83,P62,P41,P20,P21,P114,P115,P105,P84,P63,P42,P14',
'middle': 'P109,P92,P71,P50,P29,P8,P30,P9,P31,P10,P11,P32,P53,P74,P95,P94,P110,P93,P72,P51,P73,P52,P54,P33,P12,P13,P34,P55,P76,P97,P98,P77,P56,P35,P11,P96,P75,P112,P14,P111',
'bottom': 'P108,P90,P69,P48,P27,P6,P5,P26,P47,P68,P89,P88,P67,P46,P25,P4,P3,P24,P107,P87,P66,P45,P65,P44,P23,P2,P1,P22,P43,P64,P85,P86,P106,P91,P70,P49,P109,P92,P71,P50,P29,P8,P7,P28',
},
'field_centers': {'top': 'ICRS 05:35:10.465 -04.59.45.0','middle': 'ICRS 05:35:10.465 -05.22.45.0','bottom': 'ICRS 05:35:10.465 -05.44.45.0'},
'clean_depth':{'top': '0.1mJy','middle': '0.25mJy','bottom': '0.1mJy'},
'clean_depth_model':{'top': '0.5mJy','middle': '1.0mJy','bottom': '0.5mJy'},
'imsize': [16500, 18000],
}

for vis in vislist:
   initweights(vis=vis,wtmode='nyq')

keylist=['top','middle','bottom']

for i in keylist:
   os.system('rm -rf VOLS.modelgen.'+i+'.C_band.A.robust.1.0.cont*')
   tclean(vis=vislist,
       uvrange='>35klambda',
       datacolumn='data',
       field=image_data['fieldlists'][i],phasecenter=image_data['field_centers'][i],
       imagename='VOLS.modelgen.'+i+'.C_band.A.robust.1.0.cont',
       imsize=image_data['imsize'], cell=['0.125arcsec'], 
       stokes='I', specmode='mfs', gridder='mosaic', 
       mosweight=False, usepointing=False, pblimit=-0.1, deconvolver='mtmfs',
       nterms=2, restoration=True, restoringbeam=['0.5arcsec','0.5arcsec','0.0deg'], pbcor=False,
       weighting='briggs', robust=1.0, npixels=0, niter=40000,
       threshold=image_data['clean_depth_model'][i], nsigma=0.0, cyclefactor=3.0, interactive=False,
       fastnoise=True, restart=False, savemodel='none', calcres=True,
       calcpsf=True, parallel=True,usemask='auto-multithresh',
       pbmask=0.0,dogrowprune=True,minbeamfrac=0.3,sidelobethreshold=2.0,
       noisethreshold=3.75,uvtaper=['0.4arcsec'])
   #write model columnn
   tclean(vis=vislist,
       uvrange='>35klambda',
       datacolumn='data',
       field=image_data['fieldlists'][i],phasecenter=image_data['field_centers'][i],
       imagename='VOLS.modelgen.'+i+'.C_band.A.robust.1.0.cont',
       imsize=image_data['imsize'], cell=['0.125arcsec'], 
       stokes='I', specmode='mfs', gridder='mosaic', 
       mosweight=False, usepointing=False, pblimit=-0.1, deconvolver='mtmfs',
       nterms=2, restoration=True, restoringbeam=['0.5arcsec','0.5arcsec','0.0deg'], pbcor=False,
       weighting='briggs', robust=1.0, npixels=0, niter=0,
       threshold='0.0Jy', nsigma=0.0, cyclefactor=3.0, interactive=False,
       fastnoise=True,  savemodel='modelcolumn', 
       parallel=False,usemask='auto-multithresh',
       pbmask=0.0,dogrowprune=True,minbeamfrac=0.3,sidelobethreshold=2.0,
       noisethreshold=3.75,uvtaper=['0.4arcsec'],restart=True,calcres=False,calcpsf=False)

for vis in vislist:
   #uses channelized weights
   statwt(vis=vis,combine='field,scan,state,corr',chanbin=1,timebin='1yr', datacolumn='residual_data' )
for i in keylist:
   #self-calibration
   for vis in vislist:
      gaincal(vis=vis,caltable=vis+'.g',gaintype='G',calmode='p',refant='ea10',combine='spw',
              minsnr=10,refantmode='strict',solint='inf',field=image_data['fieldlists'][i])
      applycal(vis=vis,calwt=False,applymode='calonly',gaintable=vis+'.g',spwmap=32*[0],
              interp='linear',field=image_data['fieldlists'][i])


#tclean call use a clean depth shallower than what is probably desired (using the 'clean_depth_model' entry instead of 'clean_depth'
#modify if desired
for i in keylist:
   os.system('rm -rf VOLS.final.nosc.'+i+'.C_band.A.robust.1.0.cont*')
   tclean(vis=vislist,
       uvrange='>35klambda',
       datacolumn='data',
       field=image_data['fieldlists'][i],phasecenter=image_data['field_centers'][i],
       imagename='VOLS.final.nosc.'+i+'.C_band.A.robust.1.0.cont',
       imsize=image_data['imsize'], cell=['0.125arcsec'], 
       stokes='I', specmode='mfs', gridder='mosaic', 
       mosweight=False, usepointing=False, pblimit=-0.1, deconvolver='mtmfs',
       nterms=2, restoration=True, restoringbeam=['0.5arcsec','0.5arcsec','0.0deg'], pbcor=False,
       weighting='briggs', robust=1.0, npixels=0, niter=40000,
       threshold=image_data['clean_depth_model'][i], nsigma=0.0, cyclefactor=3.0, interactive=False,
       fastnoise=True, restart=False, savemodel='none', calcres=True,
       calcpsf=True, parallel=True,usemask='auto-multithresh',
       pbmask=0.0,dogrowprune=True,minbeamfrac=0.3,sidelobethreshold=2.0,
       noisethreshold=3.75,uvtaper=['0.4arcsec'])

for i in keylist:
   os.system('rm -rf VOLS.final.'+i+'.C_band.A.robust.1.0.cont*')
   tclean(vis=vislist,
       uvrange='>35klambda',
       datacolumn='corrected',
       field=image_data['fieldlists'][i],phasecenter=image_data['field_centers'][i],
       imagename='VOLS.final.'+i+'.C_band.A.robust.1.0.cont',
       imsize=image_data['imsize'], cell=['0.125arcsec'], 
       stokes='I', specmode='mfs', gridder='mosaic', 
       mosweight=False, usepointing=False, pblimit=-0.1, deconvolver='mtmfs',
       nterms=2, restoration=True, restoringbeam=['0.5arcsec','0.5arcsec','0.0deg'], pbcor=False,
       weighting='briggs', robust=1.0, npixels=0, niter=40000,
       threshold=image_data['clean_depth_model'][i], nsigma=0.0, cyclefactor=3.0, interactive=False,
       fastnoise=True, restart=False, savemodel='none', calcres=True,
       calcpsf=True, parallel=True,usemask='auto-multithresh',
       pbmask=0.0,dogrowprune=True,minbeamfrac=0.3,sidelobethreshold=2.0,
       noisethreshold=3.75,uvtaper=['0.4arcsec'])


