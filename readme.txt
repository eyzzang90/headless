## 스크립트 실행 방법

$ python chrome.py -env=local -imgSize=30720

[argument 설명]

env: 테스트 환경 (local, real)
imgSize: 이미지 파일 사이즈 (n byte 이상인 resource들에 대해서만 파일 생성)




※ 브라우저와 selenium의 Network responses 갯수가 다른 이유
ex) 네비게이션바에 있는 이미지, 롤링배너 이미지
- selenium은 html내에 있는 link element를 이용해서 데이터를 rendering하지,
    웹사이트의 root디렉토리에 위치한 파일(favicon.ico 등)은 판별할 수 없다.


