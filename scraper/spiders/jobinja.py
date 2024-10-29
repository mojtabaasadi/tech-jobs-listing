import scrapy,re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

CATEGORY_REGEX = r"\/category\/it-software-web-development-jobs"
JOBS_REGEX = r"\/companies\/[1-9a-z-_]{3,}\/jobs\/\w{3}"

class JobinjaSpider(scrapy.spiders.CrawlSpider):
    name = "jobinja"
    allowed_domains = ["jobinja.ir"]
    start_urls = [
        "https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1"
    ]

    rules = (
        Rule(link_extractor=LinkExtractor(allow=[CATEGORY_REGEX]),callback='parse_link'),
    )
    
    link_extractor = LinkExtractor(allow=JOBS_REGEX)
    
    def parse_link(self,response):
        links = response.css("a::attr('href')").getall()
        
        for link in links:
            if re.search(CATEGORY_REGEX,link):
                yield scrapy.Request(link, callback=self.parse_link)
            elif re.search(JOBS_REGEX,link):
                yield scrapy.Request(link, callback=self.parse_item)
        
    
    def parse_item(self, response):
        title,company_name,industry,company_size,company_site,category,founded_at,location,job_type,experience,salary,job_description,company_desc,skills_required,gender,military_service,education,experience = ('',)*18
        try:
            company_name = response.css('h2.c-companyHeader__name::text').get()
        except:
            pass
        try:
            industry = response.xpath('//a[@class="c-companyHeader__metaLink"][contains(@href,"/company/list")]/text()').get()
        except:
            pass
        try:
            meta = [inf.get() for inf in 
                    response.xpath('//span[@class="c-companyHeader__metaItem"]').xpath('normalize-space()')
                    if inf.get().find('تاسیس') > -1]
            founded_at = meta[0] if len(meta) else ''
        except:
            pass
        try:
            meta = [inf for inf in 
                    response.css('span.c-companyHeader__metaItem::text').getall()
                    if inf.find('نفر') > -1]
            company_size = meta[0] if len(meta) else ''
        except:
            pass
        try:
            company_site = response.css('.c-companyHeader__meta>span:last-child>a::attr(href)').get()
        except:
            pass
        try:
            title = response.css('.c-jobView__titleText>h1::text').get()
        except:
            pass
        try:
            category,location,job_type,experience,salary = response.xpath('//ul[contains(@class, "c-jobView__firstInfoBox")]//span[@class="black"]').xpath('normalize-space()').getall()
        except:
            pass
        try:
            job_description = response.xpath('//div[contains(@class, "o-box__text s-jobDesc")]').xpath('normalize-space()').get()
        except:
            pass
        try:
            company_desc = response.xpath('//div[@class="o-box__text"]').xpath('normalize-space()').get()
        except:
            pass
       
        try:
            skills_required = ','.join(response.xpath('//ul[contains(@class, "c-infoBox u-mB0")]/li[1]//span[@class="black"]').xpath('normalize-space()').getall())
        except:
            pass
        try:
            gender,military_service,education = response.xpath('//ul[contains(@class, "c-infoBox u-mB0")]/li[position() > 1]//span[@class="black"]').xpath('normalize-space()').getall()
        except:
            pass
        
        item = {
            'title':title.strip().replace('استخدام ','') if title else '',
            'company_name':company_name.strip() if company_name else '',
            'industry':industry.strip() if industry else '',
            'company_size':company_size.strip() if company_size else '',
            'company_site':company_site.strip() if company_site else '',
            'category':category.strip() if category else '','location':location.strip() if location else '',
            'job_type':job_type.strip() if job_type else '','experience':job_type.strip() if job_type else '','salary':salary.strip() if salary else '',
            'job_description':job_description.strip() if job_description else '',
            'company_desc':company_desc.strip() if company_desc else '',
            'skills_required':skills_required.strip() if skills_required else '',
            'gender':gender.strip() if gender else '','military_service':military_service.strip() if military_service else '',
            'education':education.strip() if education else '',
            'url':response.url,
            'founded_at':founded_at,
            'experience':experience.strip() if experience else ''
        }
        
        yield item
        
