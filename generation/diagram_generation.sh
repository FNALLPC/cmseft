#!/bin/bash

diagram_generation_main() {
  local name="${1:-}"
  local carddir="${2:-}"
  local prodhome="${PRODHOME:-$(pwd)}"

  if [ -z "$name" ]; then
    echo "Error: process/card name not provided" >&2
    return 1
  fi
  if [ -z "$carddir" ]; then
    echo "Error: card directory not provided" >&2
    return 1
  fi

  if [ -n "${CMSSW_BASE:-}" ]; then
    echo "Error: This script must be run in a clean environment as it sets up CMSSW itself.  You already have a CMSSW environment set up for ${CMSSW_VERSION:-unknown}." >&2
    echo "Please try again from a clean shell." >&2
    return 1
  fi

  local cardspath="${prodhome}/${carddir}"
  local proc_card="${cardspath}/${name}_proc_card.dat"
  if [ ! -f "$proc_card" ]; then
    echo "Error: process card not found: $proc_card" >&2
    return 1
  fi

  local missing_tools=()
  command -v wget >/dev/null 2>&1 || missing_tools+=("wget")
  command -v tar >/dev/null 2>&1 || missing_tools+=("tar")
  command -v sed >/dev/null 2>&1 || missing_tools+=("sed")

  local has_ps2pdf=false
  if command -v ps2pdf >/dev/null 2>&1; then
    has_ps2pdf=true
  fi

  local has_fortran=false
  local compiler
  for compiler in "${FC:-}" gfortran g77 f95 ifort; do
    if [ -n "$compiler" ] && command -v "$compiler" >/dev/null 2>&1; then
      has_fortran=true
      break
    fi
  done
  if [ "$has_fortran" = false ]; then
    missing_tools+=("Fortran compiler (gfortran, g77, f95, ifort, or FC)")
  fi

  if [ "${#missing_tools[@]}" -ne 0 ]; then
    echo "Error: missing required tool(s):" >&2
    printf '  - %s\n' "${missing_tools[@]}" >&2
    return 1
  fi

  local workdir="${prodhome}/diagrams_tmp_${name}"
  if [ -d "$workdir" ]; then
    rm -rf "$workdir"
  fi

  mkdir -p "$workdir" || return 1
  cd "$workdir" || return 1

  # Folder structure is different on CMSConnect.
  local helpers_dir="${prodhome}/Utilities"
  if [ ! -d "$helpers_dir" ]; then
    helpers_dir="$(git rev-parse --show-toplevel)/Utilities" || return 1
  fi
  source "${helpers_dir}/gridpack_helpers.sh" || return 1

  local mg_ext=".tar.gz"
  local mg="MG5_aMC_v2.9.18${mg_ext}"
  local mgsource="https://cms-project-generators.web.cern.ch/cms-project-generators/${mg}"
  local mgbasedirorig
  mgbasedirorig=$(echo "${mg%$mg_ext}" | tr "." "_")

  wget --no-check-certificate "$mgsource" || return 1
  tar xzf "$mg" || return 1
  rm "$mg"

  cd "$workdir" || return 1

  # careful: if you change the model path here, you have to change it in submit_cmsconnect_gridpack_generation(_singlejob).sh as well (model_directory)
  cp -rp "${prodhome}"/addons/models/* "${mgbasedirorig}/models/" || return 1

  if [ -e "${cardspath}/${name}_restrict_custom.dat" ]; then
    cp "${cardspath}/${name}_restrict_custom.dat" "${mgbasedirorig}/Cards/restrict_custom.dat" || return 1
    local mddir
    for mddir in "${mgbasedirorig}"/models/*/
    do
      echo "${cardspath}/${name}_restrict_custom.dat" "${mddir}/restrict_custom.dat"
      cp "${cardspath}/${name}_restrict_custom.dat" "${mddir}/restrict_custom.dat" || return 1
    done
  fi

  cp "$proc_card" "${name}_proc_card.dat" || return 1
  echo "display diagrams ./" >> "${name}_proc_card.dat"

  if ! "${mgbasedirorig}/bin/mg5_aMC" "${name}_proc_card.dat"; then
    echo "Error: MG5 failed while generating diagrams. See ${workdir}/MG5_debug if it exists." >&2
    return 1
  fi

  local nullglob_was_set=false
  if shopt -q nullglob; then
    nullglob_was_set=true
  fi
  shopt -s nullglob
  local eps_files=( *.eps )
  if [ "$nullglob_was_set" = false ]; then
    shopt -u nullglob
  fi

  if [ "${#eps_files[@]}" -eq 0 ]; then
    echo "Error: MG5 completed but did not create any EPS diagrams in $workdir" >&2
    return 1
  fi

  # remove all the zero coefficients
  sed -e "s/NP\w*=0, //g" -e "s/, SMHLOOP=0//" -e "s/NP=1, //" -i "${eps_files[@]}" || return 1

  local diagram_out="../${name}_diagrams"
  mkdir -p "$diagram_out" || return 1
  local epsfile
  if [ "$has_ps2pdf" = true ]; then
    for epsfile in "${eps_files[@]}"
    do
      ps2pdf "$epsfile" "$diagram_out/${epsfile%.*}.pdf" || return 1
    done
  else
    echo "Warning: ps2pdf not found; keeping EPS diagrams in ${prodhome}/${name}_diagrams." >&2
    for epsfile in "${eps_files[@]}"
    do
      cp "$epsfile" "$diagram_out/" || return 1
    done
  fi

  cd "$prodhome/" || return 1
  rm -rf "$workdir"
}

diagram_generation_main "$@"
diagram_generation_status=$?
unset -f diagram_generation_main
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
  return "$diagram_generation_status"
else
  exit "$diagram_generation_status"
fi
