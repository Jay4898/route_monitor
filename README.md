
# 🛡️ NX-OS CLI Configuration Human Error Guard
> **Cisco NX-OS 의도하지 않은 대형 라우팅 경로(Large Subnet) 설정 감지 및 Syslog 알람 스크립트**

![Platform](https://img.shields.io/badge/Platform-Cisco%20NX--OS-blue?style=flat-square&logo=cisco)
![Language](https://img.shields.io/badge/Language-Python%202.7%20%7C%203.x-yellow?style=flat-square&logo=python)
![Type](https://img.shields.io/badge/Type-Monitoring%20Script-green?style=flat-square)

<img src="https://github.com/user-attachments/assets/d53e4817-df67-4c9b-9118-6b0ead0827cf" width="100%" alt="Execution Example">

---

## 📖 개요 (Overview)

이 Python 스크립트는 **Cisco NX-OS 스위치**에서 실행되며, 운영자가 `running-config`에 적용했으나 아직 `startup-config`에 **저장하지 않은(Unsaved) 정적 경로(Static Route)** 변경 사항을 실시간으로 모니터링합니다.

특히, 운영자의 실수로 인해 **Prefix Length가 /24보다 작은(광범위한) 네트워크 대역**이 라우팅 테이블에 추가될 경우, 이를 즉시 감지하여 **Syslog 알람(Severity 3)**을 발생시킵니다.

<br>

## ✨ 주요 기능 (Features)

| 기능 | 설명 |
| :--- | :--- |
| **🔍 Diff 기반 모니터링** | `show running-config diff` 명령어를 사용하여, 현재 적용되었으나 저장되지 않은 변경 사항만 정밀하게 감지합니다. |
| **🛡️ 서브넷 마스크 필터링** | 단순히 경로가 추가되었다고 알람을 보내지 않고, **네트워크 대역의 크기(Prefix)**를 분석하여 위험한 경로만 선별합니다. |
| **📝 Bash Logger 연동** | NX-OS의 `bash-shell` 기능을 활용하여, 스크립트에서 발생시킨 로그가 장비의 Syslog 버퍼에 확실하게 기록되도록 보장합니다. |
| **⏰ 스케줄러 자동화** | NX-OS 자체 스케줄러(Scheduler)와 연동하여 주기적으로 자동 실행됩니다. |

### 🚦 필터링 기준 (Subnet Filtering)
* ✅ **무시 (Safe):** `/24`, `/25`, `/30`, `/32` 등 (일반적인 서브넷)
* 🚨 **경고 (Alert):** `/23`, `/22` ... `/8`, `/0` (**범위가 큰 위험 대역**)

---

## ⚙️ 사전 요구 사항 (Prerequisites)

스크립트 실행 및 로그 전송을 위해 스위치에서 다음 기능(Feature)을 활성화해야 합니다.

```bash
conf t
  feature bash-shell
  feature scheduler
end

📥 설치 방법 (Installation)
작성된 route_monitor.py 파일을 스위치의 bootflash:/ 경로로 복사합니다.

파일이 정상적으로 복사되었는지 확인합니다.

Bash
dir bootflash: | include route_monitor
🚀 사용 방법: 스케줄러 설정 (Usage)
Nexus 스위치의 내장 스케줄러(Scheduler)를 사용하여 스크립트가 주기적으로(예: 5분마다) 실행되도록 설정합니다.

1. Job 생성
스크립트를 실행할 작업을 정의합니다.

Bash
nx(config)# scheduler job name route_monitor
nx(config-job)# python bootflash:/route_monitor.py
💡 참고: NX-OS 버전에 따라 python 대신 python3 명령어를 사용해야 할 수도 있습니다.

2. Schedule 생성
정의한 Job을 얼마나 자주 실행할지 설정합니다. 아래 예시는 5분 간격으로 실행하는 설정입니다.

Bash
nx(config)# scheduler schedule name check_routes
nx(config-schedule)# job name route_monitor
nx(config-schedule)# time start now repeat 0:0:5
설정이 완료되면 스케줄러가 즉시 시작되며, 5분마다 라우팅 변경 사항을 검사합니다.

🕵️ 감지 로직 및 알람
스크립트는 매 실행 시 다음과 같은 로직으로 동작합니다.

show running-config diff 결과 중 + ip route 라인을 추출합니다.
<img width="486" height="32" alt="스크린샷 2026-02-07 오후 11 01 19" src="https://github.com/user-attachments/assets/ec6fc881-4522-4337-bc6a-f4e41a362790" />

추가된 경로의 **서브넷 마스크(Prefix Length)**를 분석합니다.

마스크 숫자가 **24 미만(0 ~ 23)**인 경우에만 **Syslog Error (Severity 3)**를 발생시킵니다.

📢 Syslog 출력 예시
/23 대역의 경로가 추가되었을 때 발생하는 로그입니다.

<img width="966" height="14" alt="스크린샷 2026-02-07 오후 11 01 00" src="https://github.com/user-attachments/assets/794942a6-469c-40b9-8ac9-7ad57e474625" />


Plaintext
2026 Feb 07 22:10:11 LEAF_1101 %USER-3-SYSTEM_MSG: UNSAVED_LARGE_NET(/23): + ip route 222.222.222.0/23 211.111.111.111 - logger
🛠️ 트러블슈팅 (Troubleshooting)
1. 스케줄러 상태 확인
스케줄러가 정상적으로 동작 중인지 확인합니다.

Bash
nx(config)# show scheduler schedule
출력 예시:

Plaintext
Schedule Name       : check_routes
--------------------------
User Name           : admin
Schedule Type       : Run every 0 Days 0 Hrs 5 Mins
Start Time          : Mon Nov 13 16:53:45 2023
Last Execution Time : Mon Nov 13 17:39:45 2023
Last Completion Time: Mon Nov 13 17:39:46 2023
Execution count     : 47
-----------------------------------------------
     Job Name            Last Execution Status
-----------------------------------------------
route_monitor                      Success (0)
2. 실행 로그 확인
Last Execution Status가 에러이거나 상세 로그를 확인하려면 아래 명령어를 사용합니다.

Bash
nx(config)# show scheduler logfile
정상 실행 로그 예시:

Plaintext
Job Name       : route_monitor                      Job Status: Success (0)
Schedule Name  : check_routes                              User Name : admin
Completion time: Mon Nov 13 17:42:46 2023
--------------------------------- Job Output ---------------------------------

python bootflash:/route_monitor.py
--- Route Diff Monitor Started ---
DEBUG: Checking for unsaved 'ip route' changes...
!!! ALERT: UNSAVED_LARGE_NET(/23): + ip route 222.222.222.0/23 211.111.111.111
DEBUG: Log sent via bash logger
--- Route Diff Monitor Finished ---
