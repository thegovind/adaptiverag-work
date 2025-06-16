
<create_file path="/home/ubuntu/repos/adaptive-rag-workbench/backend/app/ingestion/__init__.py"/>

<create_file path="/home/ubuntu/repos/adaptive-rag-workbench/backend/app/ingestion/download_10k.py">
import httpx
import asyncio
from pathlib import Path
from typing import Dict

URLS = {
    "Apple": {
        2024: "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm",
        2023: "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm",
        2022: "https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm",
        2021: "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm",
        2020: "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm",
        2019: "https://www.sec.gov/Archives/edgar/data/320193/000032019319000119/a10-k20199282019.htm"
    },
    "Google": {
        2024: "https://www.sec.gov/Archives/edgar/data/1652044/000165204424000016/goog-20231231.htm",
        2023: "https://www.sec.gov/Archives/edgar/data/1652044/000165204423000016/goog-20221231.htm",
        2022: "https://www.sec.gov/Archives/edgar/data/1652044/000165204422000019/goog-20211231.htm",
        2021: "https://www.sec.gov/Archives/edgar/data/1652044/000165204421000010/goog-20201231.htm",
        2020: "https://www.sec.gov/Archives/edgar/data/1652044/000156459020004082/goog-10k_20191231.htm",
        2019: "https://www.sec.gov/Archives/edgar/data/1652044/000165204419000004/goog10-kq42018.htm"
    },
    "Microsoft": {
        2024: "https://www.sec.gov/Archives/edgar/data/789019/000156459024003597/msft-10k_20240630.htm",
        2023: "https://www.sec.gov/Archives/edgar/data/789019/000156459023003597/msft-10k_20230630.htm",
        2022: "https://www.sec.gov/Archives/edgar/data/789019/000156459022026876/msft-10k_20220630.htm",
        2021: "https://www.sec.gov/Archives/edgar/data/789019/000156459021039151/msft-10k_20210630.htm",
        2020: "https://www.sec.gov/Archives/edgar/data/789019/000156459020034944/msft-10k_20200630.htm",
        2019: "https://www.sec.gov/Archives/edgar/data/789019/000156459019027952/msft-10k_20190630.htm"
    },
    "Meta": {
        2024: "https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/meta-20231231.htm",
        2023: "https://www.sec.gov/Archives/edgar/data/1326801/000132680123000013/meta-20221231.htm",
        2022: "https://www.sec.gov/Archives/edgar/data/1326801/000132680122000009/fb-20211231.htm",
        2021: "https://www.sec.gov/Archives/edgar/data/1326801/000132680121000014/fb-20201231.htm",
        2020: "https://www.sec.gov/Archives/edgar/data/1326801/000132680120000013/fb-20191231.htm",
        2019: "https://www.sec.gov/Archives/edgar/data/1326801/000132680119000009/fb-20181231.htm"
    },
    "JPMC": {
        2024: "https://www.sec.gov/Archives/edgar/data/19617/000001961724000070/jpm-20231231.htm",
        2023: "https://www.sec.gov/Archives/edgar/data/19617/000001961723000070/jpm-20221231.htm",
        2022: "https://www.sec.gov/Archives/edgar/data/19617/000001961722000063/jpm-20211231.htm",
        2021: "https://www.sec.gov/Archives/edgar/data/19617/000001961721000060/jpm-20201231.htm",
        2020: "https://www.sec.gov/Archives/edgar/data/19617/000001961720000052/jpm-20191231.htm",
        2019: "https://www.sec.gov/Archives/edgar/data/19617/000001961719000051/jpm-20181231.htm"
    },
    "Citi": {
        2024: "https://www.sec.gov/Archives/edgar/data/831001/000083100124000017/c-20231231.htm",
        2023: "https://www.sec.gov/Archives/edgar/data/831001/000083100123000017/c-20221231.htm",
        2022: "https://www.sec.gov/Archives/edgar/data/831001/000083100122000017/c-20211231.htm",
        2021: "https://www.sec.gov/Archives/edgar/data/831001/000083100121000017/c-20201231.htm",
        2020: "https://www.sec.gov/Archives/edgar/data/831001/000083100120000017/c-20191231.htm",
        2019: "https://www.sec.gov/Archives/edgar/data/831001/000083100119000017/c-20181231.htm"
    }
}

async def download_10k_filings():
    async with httpx.AsyncClient(timeout=60.0) as client:
        for company, years in URLS.items():
            company_dir = Path(f"data/10k/{company}")
            company_dir.mkdir(parents=True, exist_ok=True)
            
            for year, url in years.items():
                file_path = company_dir / f"{year}.html"
                if not file_path.exists():
                    try:
                        print(f"Downloading {company} {year}...")
                        response = await client.get(url)
                        response.raise_for_status()
                        file_path.write_bytes(response.content)
                        print(f"Downloaded {company} {year}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"Error downloading {company} {year}: {e}")

if __name__ == "__main__":
    asyncio.run(download_10k_filings())
