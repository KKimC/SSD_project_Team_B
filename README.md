# SSD_project_Team_B

SSD_project_Team_B

- 실행전, 터미널에서 PYTHONPATH 지정

```commandline
set PYTHONPATH=src
```

## File tree
- logs: logger 출력, 동작 시 파일 생성
- outputs: SSD 출력, 동작 시 파일 생성
- src: shell, SSD 구현
- src/utils: common functions 구현
- src/buffer: Command buffer, 동작 시 파일 생성
- tests: test cases 구현
```commandline
│  .gitignore
│  pytest.ini
│  README.md
│  requirements.txt
│
├─.github
│      pull_request_template.md
│
├─logs
├─outputs
│
├─src
│  │  command.py
│  │  command_factory.py
│  │  command_script.py
│  │  constants.py
│  │  custom_exception.py
│  │  logger.py
│  │  ssd.py
│  │  ssd_controller.py
│  │  ssd_file_manager.py
│  │  ssd_shell.py
│  │
│  ├─buffer
│  │
│  └─utils
│     │  helpers.py
│     │  validators.py
│
└─tests
    │  test_cmd_three.py
    │  test_shell.py
    │  test_shell_erase.py
    │  test_ssd.py

```

## Design Pattern
### Factory
- shell command 생성 책임을 factory에 위임
  - command 생성 추가 시 생성 변경용이성 개선

![img_4.png](img_4.png)

### Strategy
- test script 실행 책임을 receiver에 위임
  - 다양한 Test script scenario를 shell에서 일관된 방법으로 접근
  - test script 추가에 대한 변경용이성 개선

![img_5.png](img_5.png)

### Command
- shell command 이슈와 실행 책임을 command와 receiver에 위임
  - command 실행 추가 시 변경용이성 개선

![img_6.png](img_6.png)

