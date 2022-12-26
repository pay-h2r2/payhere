### framework: FastAPI

### API Spec

| HTTP Method | Path                                 | Description    | Authorization |
| ----------- | ------------------------------------ | -------------- | ------------- |
| POST        | /api/auth                            | 회원가입       |               |
| POST        | /api/auth/login                      | 로그인         |               |
| POST        | /api/auth/logout                     | 로그아웃       | O             |
| POST        | /api/auth/refresh                    | 토큰갱신       | O             |
| GET         | /api/account-books                   | 내역 전체 조회 | O             |
| GET         | /api/account-books/{account_book_id} | 특정 내역 조회 | O             |
| POST        | /api/account-books                   | 내역 작성      | O             |
| POST        | /api/account-books/duplicate         | 내역 복제      | O             |
| PATCH       | /api/account-books/{account_book_id} | 내역 수정      | O             |
| DELETE      | /api/account-books/{account_book_id} | 내역 삭제      | O             |
| POST        | /api/share                           | 단축 URL 생성  | O             |
| GET         | /api/share/{short_url}               | 단축 URL 접속  | O             |

## run

```
uvicorn main:app --reload
```

## test

```
pytest
```

# Description

## Default

- 각각의 에러는 RESPONSE BODY `detail`에 이유를 리턴합니다.
- 예외처리 되지 않은 에러는 SERVER ERROR로 봅니다.
- `Authorization`을 필요로 하는 api에서는 `JWT`를 검증하며 `ExpiredSignatureError`, `InvalidTokenError` 두 가지 에러를 토큰 에러로 봅니다.
- `access_token`의 만료 시간은 30분 이며 `refresh_token`의 만료 시간은 2일 입니다.
- `단축 URL`의 기본 만료 시간은 20분 입니다.
- `JWT` 기반의 `로그아웃`은 일반적으로 `redis`로 `blacklist` 처리한다고 알고있지만 이번에는 `dictionary`로 처리하였습니다.

#### 회원가입[POST] (/api/auth)

- Parameters: 이메일(`email`), 비밀번호(`password`)
- Errors
  - 이메일 형식이 아닐경우 `BAD REQUEST[400]`를 반환합니다.
  - 비밀번호 길이가 8 자리 미만일 경우 `BAD REQUEST[400]`를 반환합니다.
  - 중복된 이메일 일 경우 `BAD REQUEST[400]`를 반환합니다.
- Success
  - 성공 시 `CREATED[201]`를 반환 합니다.
- 비밀번호는 hash 되어 저장되며 검증을 위해 DB에는 `hashed_password`와 `salt`를 저장합니다.

#### 로그인[POST] (/api/auth/login)

- Parameters: 이메일(`email`), 비밀번호(`password`)
- Errors
  - 이메일 형식이 아닐경우 `BAD REQUEST[400]`를 반환합니다.
  - 가입된 계정이 아닐경우 `BAD REQUEST[400]`를 반환합니다.
  - 비밀번호가 다른경우 `BAD REQUEST[400]`를 반환합니다.
- Success
  - 로그아웃과 동시에 토큰 폐기를 위해 user_id에 `access_token`과 `refresh_token`을 매핑합니다.
  - `access_token`과 `refresh_token`, `OK [200]`를 반환합니다.

#### 로그아웃[POST] (/api/auth/logout)

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- 매핑된 데이터를 통해 로그인이 되어있는지 체크합니다.
- Errors
  - 로그인이 되어있지 않았을 경우 `BAD REQUEST[400]`를 반환합니다.
  - `access_token`이 최근에 갱신한 토큰과 다를경우 `UNAUTHORIZED[401]`를 반환합니다.
- Success
  - 로그인 시 저장했던 user_id에 매핑된 데이터를 삭제합니다.
  - `OK [200]`를 반환합니다.

#### 토큰갱신 [POST] (/api/auth/refresh)

- 헤더 `Authorization`에 `refresh_token`을 실어서 요청합니다.
- Errors
  - `refresh_token`이 최근에 갱신한 토큰과 다를경우 `UNAUTHORIZED[401]`를 반환합니다.
  - `access_token`이 만료되지 않았음에도 갱신 요청 시 매핑 되어있던 데이터를 모두 삭제하며 `BAD REQUEST[400]`를 반환합니다. (재로그인이 필요합니다.)
    - `refresh_token`이 탈취당했을 때의 상황을 고려하였습니다.
- Success
  - 매핑된 데이터에서 `access_token`의 정보를 갱신합니다.
  - 새로 발급된 `access_token`을 반환하며 `OK [200]`를 반환합니다.

#### 내역 전체조회 [GET] (/api/account-books)

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- JWT payload에 있는 `user_id` 를 기반으로 데이터를 조회합니다.
- Success
  - 글이 없을 경우 `NO CONTENT [204]`을 반환합니다.
  - 글이 있을 경우 전체 글 목록과 함께 `OK [200]`를 반환합니다.

#### 특정 내역조회 [GET] (/api/account-books/{account_book_id})

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- [GET] parameter `account_book_id`를 기반으로 데이터를 조회합니다.
- 공유 된 내역인지 구분하기 위해 헤더 `referer`을 확인합니다.
  - 공유 된 내역일 경우 내역 작성자를 확인하지 않으며, 게시글의 유/무 를 확인 후 적절한 응답을 합니다.
  - 공유 된 내역일 경우 `referer` 값 조작을 방지하고자 `referer`에 들어가있는 `short_url`을 확인하며, DB에 매핑되어있는 내역과 요청한 내역의 번호가 다를 시 에러를 반환합니다.
- Errors

  - share (공유된 내역)
    - 요청한 내역과 매핑되어있는 내역 번호가 다를 경우 `BAD REQUEST[400]`를 반환합니다.
  - 요청한 내역번호에 해당하는 글이 없는 경우 `BAD REQUEST[400]`를 반환합니다.
  - 요청한 내역의 작성자가 아닐경우 `BAD REQUEST[400]`를 반환합니다.

- Success
  - 요청한 내역의 정보와 `OK [200]`를 반환합니다.

#### 내역 작성 [POST] (/api/account-books)

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- Parameters: 메모(`spent_amount`), 지출 금액(`spent_amount`)
- Success
  - `account_book_id`과 `CREATED [201]`를 반환합니다.

#### 내역 복제 [POST] (/api/account-books/duplicate)

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- Parameters: 복제할 내역 번호 (`target_account_book_id`)
- 복제할 내역의 데이터 유/무를 확인합니다.
- 복제할 내역의 작성자를 확인합니다.
- 복제할 내역을 기반으로 같은 데이터를 가진 `row`를 추가합니다.
- Errors

  - 복제할 내역 번호에 해당하는 데이터가 없을 경우 `BAD REQUEST[400]`를 반환합니다.
  - 복제할 내역 번호에 해당하는 데이터의 작성자가 아닐 경우 `BAD REQUEST[400]`를 반환합니다.

- Success
  - 복제된 내역의 번호(`account_book_id`)와 함께 `CREATED [201]`를 반환합니다.

#### 내역 수정 [PATCH] (/api/account-books/{account_book_id})

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- Parameters: 메모(`spent_amount`, option), 지출 금액(`spent_amount`, option)
- `PATCH`의 특성상 부분적인 데이터 수정을 허용함으로 메모, 지출 금액은 받을 수도 안 받을 수도 있습니다.
- 수정할 내역 번호를 기반으로 데이터를 조회합니다.
- 수정할 내역의 작성자를 확인합니다.
- 수정될 `column`의 데이터를 갱신합니다.
- Errors

  - 수정할 내역 번호에 해당하는 데이터가 없을 경우 `BAD REQUEST[400]`를 반환합니다.
  - 수정할 내역 번호에 해당하는 데이터의 작성자가 아닐 경우 `BAD REQUEST[400]`를 반환합니다.

- Success
  - `OK [200]`를 반환합니다.

#### 내역 삭제 [DELETE] (/api/account-books/{account_book_id})

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- 삭제할 내역 번호를 기반으로 데이터를 조회합니다.
- 삭제할 내역의 작성자를 확인합니다.
- 데이터를 삭제합니다.
- Errors

  - 삭제할 내역 번호에 해당하는 데이터가 없을 경우 `BAD REQUEST[400]`를 반환합니다.
  - 삭제할 내역 번호에 해당하는 데이터의 작성자가 아닐 경우 `BAD REQUEST[400]`를 반환합니다.

- Success
  - `OK [200]`를 반환합니다.

#### 단축 URL 생성 [POST] (/api/share)

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- Parameters: 공유할 내역 번호(`account_book_id`), 공유 유지 시간(`expire_minutes`, option, default = `20min`)
- 공유할 내역 번호에 해당하는 데이터를 조회합니다.
- 공유할 내역의 작성자를 확인합니다.
- 공유할 내역 번호에 해당하는 단축 URL을 조회합니다.

  - 단축 URL의 정보가 있을 경우 `expired_at`을 확인하여 기존 URL의 사용 여부를 확인합니다.

- Errors

  - 공유할 내역 번호에 해당하는 데이터가 없을 경우 `BAD REQUEST[400]`를 반환합니다.
  - 공유할 내역 번호에 해당하는 데이터의 작성자가 아닐 경우 `BAD REQUEST[400]`를 반환합니다.

- Success
  - 단축 URL의 정보가 있고, URL이 만료 되지 않았다면 데이터와 `OK [200]`를 반환합니다.
  - 단축 URL의 정보가 있고, URL이 만료 되었다면 해당 `row`에 작성된 `short_url`과 `expired_at`의 정보를 갱신하며 갱신된 데이터와 `OK [200]`를 반환합니다.
  - 단축 URL의 정보가 없다면 데이터를 DB에 입력하며 데이터와 `OK [200]`를 반환합니다.
  - 반환 데이터는 `expired_at`과 `entry_url`로 구성되어 있으며 `entry_url`은 `/share/{short_url}` 와 같이 반환됩니다.

#### 단축 URL 접속 [GET] (/api/share/{short_url})

- 헤더 `Authorization`에 `access_token`을 실어서 요청합니다.
- 단축 URL의 데이터를 조회합니다.
- 단축 URL의 만료시간을 확인합니다.

- Errors

  - 단축 URL에 해당하는 데이터가 없을 경우 `BAD REQUEST[400]`를 반환합니다.
  - 단축 URL의 만료시간이 지났을 경우 `BAD REQUEST[400]`를 반환합니다.

- Success
  - `/api/account-books/{shared_account_book_id}` 로 리다이렉트 되며 `SEE OTHER [303]`을 반환합니다.
