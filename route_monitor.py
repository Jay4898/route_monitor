import sys
# -*- coding: utf-8 -*-
from syslog import LOG_WARNING, syslog
from cli import cli

def run():
    # 1. 변경된 라우팅(+ ip route) 감지
    cmd_check = 'show running-config diff | grep "+ ip route"'

    try:
        output = cli(cmd_check)

        if output:
            for line in output.splitlines():
                clean_line = line.strip()
                if not clean_line:
                    continue
                
                # --- [파싱 로직] ---
                # 예: "+ ip route 10.0.0.0/8 1.2.3.4"
                parts = clean_line.split()
                
                if len(parts) >= 4 and parts[1] == 'ip' and parts[2] == 'route':
                    prefix_part = parts[3]  # '10.0.0.0/8' 부분
                    
                    if '/' in prefix_part:
                        try:
                            # '/' 뒤의 숫자 추출
                            mask_str = prefix_part.split('/')[1]
                            mask = int(mask_str)

                            # "네트워크 대역이 /24보다 크다" == "숫자가 24보다 작다"
                            # 예: /23, /22, ... /8, /0
                            if mask < 24:
                                log_msg = "UNSAVED_LARGE_NET(/{0}): {1}".format(mask, clean_line)
                                
                                # 화면 경고
                                print("!!! ALERT: %s" % log_msg)
                                
                                # Bash Logger 전송
                                cmd_log = 'run bash logger -p local0.err "%s"' % log_msg
                                cli(cmd_log)
                                print("DEBUG: Log sent for large network (/%d)" % mask)
                                
                            else:
                                # /24, /25, /32 등은 무시
                                print("DEBUG: Ignored small network /%d (>= 24)" % mask)
                                
                        except ValueError:
                            continue
                    else:
                        continue

    except Exception:
        pass

if __name__ == "__main__":
    run()