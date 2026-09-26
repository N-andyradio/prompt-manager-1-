"""나만의 프롬프트 관리 프로그램

터미널에서 메뉴 번호를 입력해 프롬프트를 추가, 조회, 검색, 즐겨찾기 관리하는 콘솔 프로그램.
데이터는 프로그램 실행 중에만 유지된다. (종료 시 초기화)
보너스 기능으로 JSON 파일 저장/불러오기와 Markdown 내보내기를 메뉴에서 직접 실행할 수 있다.
"""

import json
from pathlib import Path

# 보너스 기능에서 사용하는 파일 경로 (프로그램 파일과 같은 폴더 기준)
BASE_DIR = Path(__file__).parent
JSON_FILE = BASE_DIR / "prompts.json"
EXPORT_DIR = BASE_DIR / "export"

# 미리 정의된 카테고리 목록
CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]

# 기본 프롬프트 데이터 (이전 미션에서 작성한 프롬프트)
# 각 프롬프트는 딕셔너리, 전체는 리스트로 관리한다.
prompts = [
    {
        "title": "블로그 글 작성 도우미",
        "content": (
            "당신은 10년 경력의 전문 블로거입니다.\n"
            "주어진 주제에 대해 SEO에 최적화된 블로그 글을 작성해주세요.\n"
            "서론, 본론, 결론 구조를 갖추고,\n"
            "독자의 관심을 끄는 제목을 3개 제안해주세요."
        ),
        "category": "텍스트 생성",
        "favorite": True,
        "views": 0,
    },
    {
        "title": "제품 썸네일 생성",
        "content": (
            "다음 제품의 매력적인 썸네일 이미지를 생성해주세요.\n"
            "제품: [제품명]\n"
            "스타일: 밝은 스튜디오 조명, 흰색 배경, 제품을 중앙에 배치\n"
            "비율: 1:1, 고해상도, 텍스트 없음"
        ),
        "category": "이미지 생성",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "IT 컨설턴트 페르소나",
        "content": (
            "당신은 중소기업 디지털 전환을 15년간 도와온 IT 컨설턴트입니다.\n"
            "전문 용어는 쉬운 비유로 풀어 설명하고,\n"
            "항상 '현재 상황 → 문제점 → 해결 방안 → 기대 효과' 순서로 답변하세요."
        ),
        "category": "페르소나",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "뉴스 요약 프롬프트",
        "content": (
            "아래 뉴스 기사를 읽고 다음 형식으로 요약해주세요.\n"
            "1. 한 줄 요약\n"
            "2. 핵심 내용 3가지 (불릿)\n"
            "3. 관련 키워드 5개\n"
            "[기사 본문]"
        ),
        "category": "자동화",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "광고 스크립트 작성",
        "content": (
            "30초 분량의 제품 광고 영상 스크립트를 작성해주세요.\n"
            "장면 번호, 화면 설명, 내레이션, 자막을 표 형식으로 정리하고,\n"
            "처음 3초 안에 시청자의 시선을 사로잡는 훅을 넣어주세요."
        ),
        "category": "영상 생성",
        "favorite": False,
        "views": 0,
    },
]


# ---------------------------------------------------------------------------
# 입력 도우미 함수
# ---------------------------------------------------------------------------

def input_not_empty(label):
    """값이 입력될 때까지 반복해서 입력을 요청하고, 앞뒤 공백을 제거한 값을 돌려준다."""
    while True:
        value = input(label).strip()
        if value:
            return value
        print("값이 비어 있습니다. 다시 입력해주세요.")


def print_categories():
    """카테고리 목록을 번호와 함께 출력한다."""
    for number, category in enumerate(CATEGORIES, start=1):
        print(f"{number}) {category}")


def choose_category(allow_custom=True):
    """카테고리를 번호로 선택하거나 직접 입력받아 카테고리 이름을 돌려준다.

    allow_custom이 True이면 목록에 없는 카테고리를 직접 입력할 수 있다.
    """
    while True:
        print("\n카테고리 선택:")
        print_categories()
        if allow_custom:
            print("(목록에 없으면 카테고리 이름을 직접 입력하세요)")
        choice = input_not_empty("선택: ")

        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        if allow_custom and not choice.isdigit():
            return choice
        print("잘못된 번호입니다. 다시 선택해주세요.")


def input_prompt_index(label="번호 입력: "):
    """프롬프트 번호를 입력받아 리스트 인덱스를 돌려준다.

    프롬프트가 없거나 잘못된 번호를 입력하면 안내 메시지를 출력하고 None을 돌려준다.
    """
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return None

    choice = input(label).strip()
    if choice.isdigit() and 1 <= int(choice) <= len(prompts):
        return int(choice) - 1

    print(f"잘못된 번호입니다. 1 ~ {len(prompts)} 사이의 번호를 입력해주세요.")
    return None


# ---------------------------------------------------------------------------
# 출력 도우미 함수
# ---------------------------------------------------------------------------

def format_prompt_line(number, prompt):
    """목록 한 줄을 '번호. [카테고리] 제목 ⭐' 형식의 문자열로 만든다."""
    star = " ⭐" if prompt["favorite"] else ""
    return f"{number}. [{prompt['category']}] {prompt['title']}{star}"


def print_prompt_list(indexes):
    """전달받은 인덱스의 프롬프트들을 전체 목록 기준 번호와 함께 출력한다.

    번호를 전체 목록 기준으로 보여주기 때문에, 검색/카테고리 결과에서 본 번호를
    그대로 상세 보기나 즐겨찾기 관리에 사용할 수 있다.
    """
    for index in indexes:
        print(format_prompt_line(index + 1, prompts[index]))


# ---------------------------------------------------------------------------
# 기능 함수
# ---------------------------------------------------------------------------

def add_prompt():
    """제목, 내용, 카테고리를 입력받아 새 프롬프트를 리스트에 추가한다."""
    print("\n=== 프롬프트 추가 ===")
    title = input_not_empty("제목: ")
    content = input_not_empty("내용: ")
    category = choose_category()

    new_prompt = {
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,  # 즐겨찾기 기본값은 False
        "views": 0,  # 상세 보기 횟수 (보너스)
    }
    prompts.append(new_prompt)
    print("\n프롬프트가 추가되었습니다!")


def show_list():
    """저장된 모든 프롬프트를 번호와 함께 출력한다."""
    print("\n=== 프롬프트 목록 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다. 먼저 프롬프트를 추가해주세요.")
        return

    print_prompt_list(range(len(prompts)))
    print(f"\n총 {len(prompts)}개의 프롬프트")


def get_all_categories():
    """기본 카테고리에 사용자가 직접 입력한 카테고리를 더한 목록을 돌려준다."""
    categories = list(CATEGORIES)
    for prompt in prompts:
        if prompt["category"] not in categories:
            categories.append(prompt["category"])
    return categories


def show_by_category():
    """카테고리를 선택받아 해당 카테고리의 프롬프트만 출력한다."""
    print("\n=== 카테고리별 조회 ===")
    categories = get_all_categories()
    for number, category in enumerate(categories, start=1):
        print(f"{number}) {category}")

    choice = input("선택: ").strip()
    if not (choice.isdigit() and 1 <= int(choice) <= len(categories)):
        print("잘못된 번호입니다. 메뉴로 돌아갑니다.")
        return

    selected = categories[int(choice) - 1]
    indexes = [i for i, prompt in enumerate(prompts) if prompt["category"] == selected]

    if not indexes:
        print(f"\n[{selected}] 카테고리에 등록된 프롬프트가 없습니다.")
        return

    print(f"\n[{selected}] 카테고리 프롬프트:")
    print_prompt_list(indexes)
    print(f"\n총 {len(indexes)}개의 프롬프트")


def search_prompt():
    """키워드가 제목 또는 내용에 포함된 프롬프트를 찾아 출력한다. (대소문자 무시)"""
    print("\n=== 프롬프트 검색 ===")
    keyword = input_not_empty("검색어: ").lower()

    indexes = []
    for i, prompt in enumerate(prompts):
        if keyword in prompt["title"].lower() or keyword in prompt["content"].lower():
            indexes.append(i)

    if not indexes:
        print(f"\n'{keyword}'에 해당하는 프롬프트가 없습니다.")
        return

    print("\n검색 결과:")
    print_prompt_list(indexes)
    print(f"\n{len(indexes)}개의 프롬프트를 찾았습니다.")


def show_detail():
    """번호를 입력받아 해당 프롬프트의 전체 내용을 출력한다."""
    print("\n=== 프롬프트 상세 보기 ===")
    index = input_prompt_index()
    if index is None:
        return

    prompt = prompts[index]
    prompt["views"] += 1  # 상세 보기를 할 때마다 조회수 1 증가

    line = "─" * 40
    print()
    print(line)
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {'⭐' if prompt['favorite'] else '-'}")
    print(f"조회수: {prompt['views']}회")
    print(line)
    print("내용:")
    print(prompt["content"])
    print(line)


def toggle_favorite():
    """번호를 입력받아 해당 프롬프트의 즐겨찾기를 추가하거나 해제한다."""
    print("\n=== 즐겨찾기 관리 ===")
    show_list()
    print()
    index = input_prompt_index("프롬프트 번호 입력: ")
    if index is None:
        return

    prompt = prompts[index]
    prompt["favorite"] = not prompt["favorite"]  # True <-> False 전환
    if prompt["favorite"]:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에 추가했습니다!")
    else:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에서 해제했습니다.")


def show_favorites():
    """즐겨찾기된 프롬프트만 모아서 출력한다."""
    print("\n=== 즐겨찾기 목록 ===")
    indexes = [i for i, prompt in enumerate(prompts) if prompt["favorite"]]

    if not indexes:
        print("즐겨찾기한 프롬프트가 없습니다. '6. 즐겨찾기 관리'에서 추가해보세요.")
        return

    print_prompt_list(indexes)
    print(f"\n총 {len(indexes)}개의 즐겨찾기")


# ---------------------------------------------------------------------------
# 보너스 2 - 수정 / 삭제 / 조회수 TOP
# ---------------------------------------------------------------------------

def edit_prompt():
    """번호를 입력받아 프롬프트의 제목, 내용, 카테고리를 수정한다.

    아무것도 입력하지 않고 Enter를 누르면 기존 값을 그대로 유지한다.
    """
    print("\n=== 프롬프트 수정 ===")
    index = input_prompt_index("수정할 프롬프트 번호: ")
    if index is None:
        return

    prompt = prompts[index]
    print("(변경하지 않으려면 그냥 Enter를 누르세요)")
    new_title = input(f"제목 [{prompt['title']}]: ").strip()
    new_content = input("내용 (새 내용 입력): ").strip()
    change_category = input(f"카테고리 [{prompt['category']}] 변경할까요? (y/N): ").strip().lower()

    if new_title:
        prompt["title"] = new_title
    if new_content:
        prompt["content"] = new_content
    if change_category == "y":
        prompt["category"] = choose_category()

    print(f"\n'{prompt['title']}' 프롬프트가 수정되었습니다!")


def delete_prompt():
    """번호를 입력받아 확인 후 프롬프트를 삭제한다."""
    print("\n=== 프롬프트 삭제 ===")
    index = input_prompt_index("삭제할 프롬프트 번호: ")
    if index is None:
        return

    title = prompts[index]["title"]
    answer = input(f"'{title}' 프롬프트를 정말 삭제할까요? (y/N): ").strip().lower()
    if answer != "y":
        print("삭제를 취소했습니다.")
        return

    prompts.pop(index)
    print(f"'{title}' 프롬프트를 삭제했습니다.")


def show_top(limit=5):
    """조회수가 높은 순서로 상위 프롬프트를 출력한다."""
    print(f"\n=== 인기 프롬프트 TOP {limit} ===")
    viewed = [i for i, prompt in enumerate(prompts) if prompt["views"] > 0]
    if not viewed:
        print("아직 조회된 프롬프트가 없습니다. '5. 프롬프트 상세 보기'로 조회해보세요.")
        return

    # 조회수 기준 내림차순 정렬
    viewed.sort(key=lambda i: prompts[i]["views"], reverse=True)
    for rank, index in enumerate(viewed[:limit], start=1):
        prompt = prompts[index]
        print(f"{rank}위. {format_prompt_line(index + 1, prompt)} (조회 {prompt['views']}회)")


# ---------------------------------------------------------------------------
# 보너스 1 - JSON 저장/불러오기, Markdown 내보내기
# ---------------------------------------------------------------------------

def save_to_json():
    """현재 프롬프트 목록을 JSON 파일로 저장한다."""
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=2)
    print(f"\n{len(prompts)}개의 프롬프트를 저장했습니다: {JSON_FILE.name}")


def load_from_json():
    """JSON 파일에서 프롬프트 목록을 불러와 현재 목록을 교체한다."""
    if not JSON_FILE.exists():
        print(f"\n저장된 파일이 없습니다. 먼저 'JSON 저장'을 실행해주세요. ({JSON_FILE.name})")
        return

    try:
        with open(JSON_FILE, encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("\nJSON 파일 형식이 올바르지 않아 불러올 수 없습니다.")
        return

    loaded = []
    for item in data:
        # 필수 항목이 없는 데이터는 건너뛰고, 선택 항목은 기본값을 채운다.
        if not all(key in item for key in ("title", "content", "category")):
            continue
        item.setdefault("favorite", False)
        item.setdefault("views", 0)
        loaded.append(item)

    prompts[:] = loaded  # 리스트 내용 자체를 교체 (global 없이 수정)
    print(f"\n{len(loaded)}개의 프롬프트를 불러왔습니다.")


def export_markdown():
    """전체 프롬프트를 카테고리별 Markdown 파일로 내보낸다."""
    if not prompts:
        print("\n내보낼 프롬프트가 없습니다.")
        return

    EXPORT_DIR.mkdir(exist_ok=True)
    for category in get_all_categories():
        items = [prompt for prompt in prompts if prompt["category"] == category]
        if not items:
            continue

        lines = [f"# {category}", ""]
        for prompt in items:
            star = " ⭐" if prompt["favorite"] else ""
            lines.append(f"## {prompt['title']}{star}")
            lines.append("")
            lines.append("```")
            lines.append(prompt["content"])
            lines.append("```")
            lines.append("")

        # 파일 이름에 쓸 수 없는 문자는 '_'로 바꾼다.
        safe_name = "".join("_" if ch in '\\/:*?"<>|' else ch for ch in category)
        path = EXPORT_DIR / f"{safe_name}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"내보내기 완료: {path.relative_to(BASE_DIR)} ({len(items)}개)")


# ---------------------------------------------------------------------------
# 메뉴 / 메인 루프
# ---------------------------------------------------------------------------

def show_menu():
    """메인 메뉴를 출력한다."""
    print()
    print("=== 나만의 프롬프트 관리 ===")
    print("1. 프롬프트 추가")
    print("2. 프롬프트 목록")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 프롬프트 상세 보기")
    print("6. 즐겨찾기 관리")
    print("7. 즐겨찾기 목록")
    print("8. 프롬프트 수정")
    print("9. 프롬프트 삭제")
    print("10. 인기 프롬프트 TOP 5")
    print("11. JSON 파일로 저장")
    print("12. JSON 파일에서 불러오기")
    print("13. 카테고리별 Markdown 내보내기")
    print("0. 종료")


def main():
    """메뉴를 반복해서 보여주고, 입력한 번호에 맞는 기능을 실행한다."""
    while True:
        show_menu()
        choice = input("선택: ").strip()

        # match-case는 Python 3.10 이상에서 사용할 수 있는 문법이다.
        match choice:
            case "1":
                add_prompt()
            case "2":
                show_list()
            case "3":
                show_by_category()
            case "4":
                search_prompt()
            case "5":
                show_detail()
            case "6":
                toggle_favorite()
            case "7":
                show_favorites()
            case "8":
                edit_prompt()
            case "9":
                delete_prompt()
            case "10":
                show_top()
            case "11":
                save_to_json()
            case "12":
                load_from_json()
            case "13":
                export_markdown()
            case "0":
                print("프로그램을 종료합니다. 안녕히 가세요!")
                break
            case _:
                print("잘못된 번호입니다. 메뉴에 있는 번호를 입력해주세요.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 또는 입력 스트림 종료 시 오류 메시지 대신 정상 종료 안내를 보여준다.
        print("\n\n프로그램을 종료합니다. 안녕히 가세요!")
