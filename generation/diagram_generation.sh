#!/bin/bash -x

#First you need to set couple of settings:
name=${1}
# name of the run
carddir=${2}

if [ -z "$PRODHOME" ]; then
  PRODHOME=`pwd`
fi

CARDSDIR=${PRODHOME}/${carddir}


WORKDIR=$PRODHOME/diagrams_tmp_${name}
if [ -d $WORKDIR ]; then
    rm -rf $WORKDIR
fi

mkdir -p $WORKDIR
cd $WORKDIR

# Folder structure is different on CMSConnect
helpers_dir=${PRODHOME}/Utilities
if [ ! -d "$helpers_dir" ]; then
    helpers_dir=$(git rev-parse --show-toplevel)/Utilities
fi
source ${helpers_dir}/gridpack_helpers.sh

if [ ! -z ${CMSSW_BASE} ]; then
  echo "Error: This script must be run in a clean environment as it sets up CMSSW itself.  You already have a CMSSW environment set up for ${CMSSW_VERSION}."
  echo "Please try again from a clean shell."
  if [ "${BASH_SOURCE[0]}" != "${0}" ]; then return 1; else exit 1; fi
fi

#catch unset variables
set -u

if [ -z ${name} ]; then
  echo "Process/card name not provided"
  if [ "${BASH_SOURCE[0]}" != "${0}" ]; then return 1; else exit 1; fi
fi

MG_EXT=".tar.gz"
MG=MG5_aMC_v2.6.5$MG_EXT
MGSOURCE=https://cms-project-generators.web.cern.ch/cms-project-generators/$MG
MGBASEDIRORIG=$(echo ${MG%$MG_EXT} | tr "." "_")
wget --no-check-certificate ${MGSOURCE}
tar xzf ${MG}
rm "$MG"

cd $WORKDIR

# careful: if you change the model path here, you have to change it in submit_cmsconnect_gridpack_generation(_singlejob).sh as well (model_directory)
cp -rp ${PRODHOME}/addons/models/* ${MGBASEDIRORIG}/models/

if [ -e $CARDSDIR/${name}_restrict_custom.dat ]; then
  cp $CARDSDIR/${name}_restrict_custom.dat ./Cards/restrict_custom.dat
  for MDDIR in ${MGBASEDIRORIG}/models/*/
  do
      echo $CARDSDIR/${name}_restrict_custom.dat $MDDIR/restrict_custom.dat 
      cp $CARDSDIR/${name}_restrict_custom.dat $MDDIR/restrict_custom.dat
  done
fi

cp $CARDSDIR/${name}_proc_card.dat ${name}_proc_card.dat
echo "display diagrams ./" >> ${name}_proc_card.dat

${MGBASEDIRORIG}/bin/mg5_aMC ${name}_proc_card.dat

# remove all the zero coefficients
sed -e "s/NP\w*=0, //g" -e "s/, SMHLOOP=0//" -e "s/NP=1, //" -i *.eps

PDFOUT="../${name}_diagrams"
mkdir -p $PDFOUT
for epsfile in *.eps 
do
    ps2pdf $epsfile $PDFOUT/${epsfile%.*}.pdf
done

cd $PRODHOME/
rm -rf $WORKDIR
