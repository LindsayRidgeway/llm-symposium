#!/usr/bin/env bash
# rover-check — first-boot report for a Picar-X body. READ-ONLY: it fixes nothing, it just says
# what is there and what is missing, so a new body can be brought up without guessing.
#
# Written 2026-09-26 for Gemini's rover: the card is imaged, the chassis is being assembled, and
# when the Pi comes up this is the one command that says what still needs doing.
#
#   bash rover-check.sh            # report
#   bash rover-check.sh --json     # same, as one JSON object (for a log or a diff between bodies)
#
# Note: importing picarx resets the Robot HAT's MCU, which mutes the speaker amplifier, so the
# speaker enable is re-run afterwards. That is not a fault, it is the HAT's design.

JSON=0
[ "${1:-}" = "--json" ] && JSON=1
R=()
say() { [ "$JSON" = 0 ] && printf '%-34s %s\n' "$1" "$2"; R+=("$1|$2"); }

if [ "$JSON" = 0 ]; then
  echo "== rover-check $(date '+%Y-%m-%d %H:%M') =="
fi

say hostname        "$(hostname)"
say os              "$(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || echo unknown)"
say kernel          "$(uname -r)"
say model           "$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo unknown)"
say python3         "$(python3 -V 2>&1 | cut -d' ' -f2)"

# --- libraries -----------------------------------------------------------------
if python3 -c 'import picarx' 2>/dev/null; then say picarx_lib ok; else say picarx_lib MISSING; fi
if python3 -c 'import robot_hat' 2>/dev/null; then say robot_hat_lib ok; else say robot_hat_lib MISSING; fi
python3 -c 'import robot_hat' 2>/dev/null && /usr/local/bin/robot_hat enable_speaker >/dev/null 2>&1

# --- camera --------------------------------------------------------------------
CAM="$(timeout 20 rpicam-hello --list-cameras 2>&1 | sed -n 's/^ *0 *: *\([a-z0-9_]*\).*/\1/p' | head -1)"
if [ -n "$CAM" ]; then say camera_detected "$CAM"; else say camera_detected NONE; fi
say camera_legacy "$( (vcgencmd get_camera 2>/dev/null || echo 'vcgencmd unavailable') )"
say asoundrc       "$( [ -f "$HOME/.asoundrc" ] && echo present || echo MISSING )"

# --- speaker / voice -----------------------------------------------------------
say amp_service    "$(systemctl is-enabled robot-hat-speaker.service 2>/dev/null || echo MISSING)"
say amp_active     "$(systemctl is-active robot-hat-speaker.service 2>/dev/null || echo inactive)"
say piper_bin      "$( [ -x /usr/local/bin/piper ] && echo /usr/local/bin/piper || echo MISSING )"
say piper_models   "$(ls "$HOME/.piper_models"/*.onnx 2>/dev/null | wc -l | tr -d ' ') model(s)"
say aplay          "$( [ -x /usr/bin/aplay ] && echo ok || echo MISSING )"

# --- hardware readings (a live body, not a spec) --------------------------------
READ="$(timeout 25 python3 - <<'PY' 2>/dev/null
from picarx import Picarx
from robot_hat import ADC
px = Picarx()
try:
    print('distance=%s' % px.get_distance())
    print('grayscale=%s' % px.get_grayscale_data())
    print('battery_raw=%s' % ADC('A4').read())
except Exception as e:
    print('read_error=%r' % e)
PY
)"
echo "$READ" | grep -q . && while read -r l; do say "hw_${l%%=*}" "${l#*=}"; done <<< "$READ" \
  || say hw_read FAILED
/usr/local/bin/robot_hat enable_speaker >/dev/null 2>&1

# --- control layer --------------------------------------------------------------
say pilot_script   "$( [ -f "$HOME/rover-pilot.py" ] && echo present || echo MISSING )"
say pilot_running  "$(pgrep -f rover-pilot.py >/dev/null && echo yes || echo no)"
say authorized_keys "$( [ -f "$HOME/.ssh/authorized_keys" ] && wc -l < "$HOME/.ssh/authorized_keys" | tr -d ' ' || echo 0 ) key(s)"
say disk_free      "$(df -h / | awk 'NR==2{print $4}')"
say mem_free       "$(free -h 2>/dev/null | awk '/Mem:/{print $7}')"

if [ "$JSON" = 1 ]; then
  printf '{'
  first=1
  for item in "${R[@]}"; do
    k="${item%%|*}"; v="${item#*|}"
    [ "$first" = 0 ] && printf ','
    first=0
    printf '"%s":"%s"' "$k" "$(printf '%s' "$v" | sed 's/"/\\"/g')"
  done
  printf '}\n'
fi
