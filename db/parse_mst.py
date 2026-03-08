"""
한국투자증권 종목 마스터 파일(.mst) 파싱 스크립트
KOSPI, KOSDAQ 종목 정보를 파싱하여 SQL INSERT 문을 생성합니다.
"""
import sys
import os

def parse_mst_file(file_path, market_type):
    """
    .mst 파일을 파싱하여 종목 정보 추출

    Args:
        file_path: mst 파일 경로
        market_type: 'KOSPI' 또는 'KOSDAQ'

    Returns:
        list of tuples: (종목코드, 종목명, 시장구분, 업종)
    """
    stocks = []

    try:
        with open(file_path, 'rb') as f:
            for line in f:
                try:
                    # CP949 디코딩
                    decoded_line = line.decode('cp949', errors='ignore')

                    if len(decoded_line) < 100:  # 최소 길이 체크
                        continue

                    # 한국투자증권 mst 파일 포맷 (고정길이)
                    # 종목코드: 위치 0-6 (6자리)
                    stock_code = decoded_line[0:6].strip()

                    # ISIN 코드 건너뛰기: 위치 9-21
                    # 종목명: 위치 21-61 (40자)
                    stock_name_raw = decoded_line[21:61].strip()

                    # 종목명만 추출 (ST, BC, DR, FS 등 구분자 전까지)
                    # 공백으로 구분하여 첫 번째 부분만 (순수 종목명)
                    stock_name = stock_name_raw.split()[0] if stock_name_raw else ""

                    # 숫자로 시작하는 종목코드만 (일반 주식)
                    if stock_code and len(stock_code) == 6 and stock_code.isdigit():
                        # 종목명에서 특수문자 제거
                        stock_name = stock_name.replace("'", "''")  # SQL 이스케이프

                        # ETF, ETN 등 제외하고 순수 주식만
                        exclude_keywords = ['스팩', 'SPAC', 'ETN', '리츠', 'KODEX', 'TIGER', 'ARIRANG', 'KINDEX']
                        if not any(keyword in stock_name for keyword in exclude_keywords):
                            stocks.append((stock_code, stock_name, market_type))

                except Exception as e:
                    continue

    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return []

    return stocks

def generate_sql_inserts(stocks):
    """
    종목 리스트를 SQL INSERT 문으로 변환

    Args:
        stocks: list of tuples (종목코드, 종목명, 시장구분)

    Returns:
        str: SQL INSERT 문
    """
    if not stocks:
        return ""

    sql_lines = []
    sql_lines.append("-- 종목 정보 자동 생성 (mst 파일 파싱)")
    sql_lines.append("INSERT INTO stocks (stock_code, stock_name, market, sector) VALUES")

    values = []
    for stock_code, stock_name, market in stocks:
        # 업종은 나중에 API로 가져올 예정이므로 NULL
        values.append(f"    ('{stock_code}', '{stock_name}', '{market}', NULL)")

    sql_lines.append(",\n".join(values))
    sql_lines.append("ON CONFLICT (stock_code) DO NOTHING;")

    return "\n".join(sql_lines)

def main():
    """메인 실행 함수"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # mst 파일 경로 (절대 경로)
    kospi_file = os.path.join(project_root, 'api_docs', '종목정보', 'kospi_code.mst')
    kosdaq_file = os.path.join(project_root, 'api_docs', '종목정보', 'kosdaq_code.mst')

    print("=" * 60)
    print("한국투자증권 종목 마스터 파일 파싱 시작")
    print("=" * 60)

    # KOSPI 파싱
    print(f"\n[1/2] KOSPI 종목 파싱 중...")
    kospi_stocks = parse_mst_file(kospi_file, 'KOSPI')
    print(f"  → {len(kospi_stocks)}개 종목 추출 완료")

    # KOSDAQ 파싱
    print(f"\n[2/2] KOSDAQ 종목 파싱 중...")
    kosdaq_stocks = parse_mst_file(kosdaq_file, 'KOSDAQ')
    print(f"  → {len(kosdaq_stocks)}개 종목 추출 완료")

    # 전체 종목
    all_stocks = kospi_stocks + kosdaq_stocks
    print(f"\n총 {len(all_stocks)}개 종목 파싱 완료")

    # SQL 생성
    output_file = os.path.join(script_dir, 'stocks_data.sql')
    sql_content = generate_sql_inserts(all_stocks)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)

    print(f"\n✓ SQL 파일 생성 완료: {output_file}")
    print("=" * 60)

    # 샘플 출력 (처음 5개)
    print("\n[샘플] 처음 5개 종목:")
    for i, (code, name, market) in enumerate(all_stocks[:5], 1):
        print(f"  {i}. [{market}] {code} - {name}")

if __name__ == "__main__":
    main()
