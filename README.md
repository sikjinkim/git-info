# git 기본 명령어
### 현재 상태 확인
* 관리되고 있는 파일과 디렉토리 목록을 확인할 수 있다.
![image](https://user-images.githubusercontent.com/71370540/215632608-5c72d01a-4d46-498b-98cd-bceadca5c0e4.png)


### 전체 로그 확인
* 커밋 기록을 조회할 수 있다.
* -p : 각 커밋의 diff결과를 보여준다.
* -숫자 : 선택한 숫자만큼의 최근 내역의 보여준다.
![image](https://user-images.githubusercontent.com/71370540/215632755-ccc27195-2b8d-47d6-b790-c999c50b572b.png)


### git 저장소 생성
* 현재 디렉토리 기준으로 git 저장소가 생성된다.
![image](https://user-images.githubusercontent.com/71370540/215632876-48504ccd-aa92-4280-9f6b-c1f29d4a5aac.png)


### 저장소 복제 및 다운로드
* 원격의 저장소를 복사해온다.
![image](https://user-images.githubusercontent.com/71370540/215633029-06f9bd10-303a-499f-b819-ef27d6e94fa7.png)


### 저장소에 코드 추가
* 작업 디렉토리상의 변경 내용을 스테이징 영역에 추가하기 위해서 사용한다.
* -A : 작업 디렉토리 내의 모든 변경 내용을 모두 스테이징 영역으로 넘긴다.
* -p : 각 변경사항을 터미널에서 하나씩 확인하면서 스테이징 영역으로 넘긴다.
* . : 현재 디렉토리의 모든 변경 내용을 스테이징 영역으로 넘긴다.
![image](https://user-images.githubusercontent.com/71370540/215638674-24197f1e-dd0b-4772-9cfa-9be5a3115de1.png)


### 커밋 생성
* 작업한 파일을 commit한다.
* -m : -m 뒤에 ""를 포함한 메세지를 입력하여 설명을 추가한다.
![image](https://user-images.githubusercontent.com/71370540/215639977-44403cd9-cf86-4f61-98d6-6a9567852708.png)


### 변경 사항 원격 서버 업로드
* git commit 후에 변경 이력을 저장한다.
* -u : push할 때 -u 옵션을 사용하면 후에 push할때는 <원격저장소 명>과 <브랜치 명>을 입력한지 않아도 된다.
![image](https://user-images.githubusercontent.com/71370540/215640347-bb4ded9c-c68e-43b6-bd47-41cad389c04b.png)


### 원격 저장소의 변경 내용을 현재 디렉토리로 가져옴
* 원격 저장소의 소스를 로컬 저장소로 내려받는다.
* -rebase : 원격 저장소의 commit이력이 로컬 저장소로 합쳐지고, 로컬 저장소의 변경사항이 재반영된다.
![image](https://user-images.githubusercontent.com/71370540/215642924-ad4cc7a7-a14b-4afd-b04d-29d525dc2ef0.png)


### 변경 내용을 merge 하기 전에 바뀐 내용 비교
* commit이나 branch 사이에 다른점 혹은 파일이나 repository와 working directory 사이의 다른점을 보여준다.
![image](https://user-images.githubusercontent.com/71370540/215651223-34273775-8b1c-4af1-90ed-2d405359e165.png)




# branch 관련
### github 주소와 연결
* 등록된 리모트 저장소 이름만 보여준다.
* -v : 등록된 저장소 이름과 URL을 표시한다.
* add <리모트 이름> (경로>) : 새 리모트를 추가한다. (경로)에는 URL이나 파일 경로를 넣을 수 있다.
* show (리모트 이름) : 모든 리모트 경로의 branch 정보를 표시한다.
* rm (리모트 이름) : 리모트 경로를 제거한다.
![image](https://user-images.githubusercontent.com/71370540/215651845-9a347924-9533-4822-a3d0-65eeddbd8861.png)


### 브랜치 생성

![image](https://user-images.githubusercontent.com/71370540/215652447-bf64e9f3-b96b-4c45-a54f-c76e29924e9d.png)



