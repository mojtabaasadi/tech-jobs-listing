import scrapy,json
from scrapy.selector import Selector 
from scrapy.http import Response


class JobvisionSpider(scrapy.Spider):
    name = "jobvision"
    allowed_domains = ["jobvision.ir"]
    start_urls = ["https://jobvision.ir/jobs/category/developer"]
    
    def parse(self, response):
        dt = {"pageSize":30,"requestedPage": 1,"jobCategoryUrlTitle":"developer","sortBy":1,"searchId":None}
        yield scrapy.Request("https://candidateapi.jobvision.ir/api/v1/JobPost/List",
                                 callback=self.parse_list,method='POST',body=json.dumps(dt),
                                 headers={'Content-Type':'application/json'})

    def parse_list(self, response):
        
        data = json.loads(response.text)

        
        for item in data['data']['jobPosts']:
            yield scrapy.Request('https://jobvision.ir/jobs/'+str(item['id']),callback=self.parse_item)    
        
        total_pages = data['data']['jobPostCount'] / data['data']['pageSize']
        current_page = data['data']['currentPage']
        
        if total_pages > current_page:
            dt = {"pageSize":30,"requestedPage":
            current_page + 1,"jobCategoryUrlTitle":"developer","sortBy":1,"searchId":None}
            yield scrapy.Request("https://candidateapi.jobvision.ir/api/v1/JobPost/List",
                                 callback=self.parse_list,method='POST',body=json.dumps(dt),
                                 headers={'Content-Type':'application/json'})

            
    def parse_item(self,response):
        (title,company_name,industry,company_size,company_site,category,
         founded_at,location,job_type,experience,salary,job_description,company_desc,
         skills_required,gender,military_service,education,experience,age_range) = ('',)*19
        body_str = response.xpath('//script[@id="serverApp-state"]/text()').get()
        body = json.loads(body_str)
        key = [k for k in body.keys() if k.find('JobPost/Detail?') >-1 ][0]
        data = body[key]
        try:
            company_name = data['company']['name']['titleFa']
        except:
            pass
        try:
            title = data['title']
        except:
            pass
        try:
            industry = data['company']['industries'][0]['titleFa']
        except:
            pass
        try:
            company_size = data['company']['size']['titleFa']
        except:
            pass
        try:
            company_site = data['company']['website']
        except:
            pass
        try:
            founded_at = data['company']['establishmentYear']
        except:
            pass
        try:
            location = data['location']['city']['titleFa']
        except:
            pass
        try:
            job_type = data['workType']['titleFa']
        except:
            pass
        try:
            experience = data['scoreOfWorkExperienceInJobCategory']['expectedValue']
        except: 
            pass
        try:
            job_description = data['description']
        except:
            pass
        try:
            salary = data['salary']['titleFa']
        except:
            pass
        skills_required = []
        try:
            if len(data['academicRequirements']):
                education = [a['degreeLevel']['titleFa'] + ' در ' + a['academicField']['titleFa'] for a in
                            data['academicRequirements']]
                skills_required += education
                
            if data['languageRequirements']:
                skills_required += [a['skill']['titleFa'] + ' در '+a['language']['titleFa']
                                                            for a in
                                                            data['languageRequirements']
                                                            ] 
            if data['softwareRequirements']:
                skills_required += [a['software']['titleFa']+' '+a['skill']['titleFa'] for a in data['softwareRequirements']]
        except:
            pass
        
        
        try:
            company_desc = data['company']['description']['titleFa']
        except:
            pass
        try:
            gender = data['geneder']['titleFa']
        except:
            pass
        try:
            military_service  = "پایان خدمت یا معاف" if data['shouldDoneMilitaryService'] else "مهم نیست"
        except:
            pass        
        try:
            age_range =  '{0} تا  {1}'.format(
                data['requiredAgeMin'] if data['requiredAgeMin'] else '' ,
                data['requiredAgeMax'] if data['requiredAgeMax'] else '') 
        except:
            pass
        
        yield {
            'title':title,
            'company_name':company_name,
            'industry':industry,
            'company_size':company_size,
            'company_site':company_site,
            'category':category,
            'founded_at':founded_at,
            'location':location,
            'job_type':job_type,
            'experience':experience,
            'url':response.url,
            'salary':salary,
            'job_description': Selector(text=job_description).xpath('string(//*)').get(),
            'company_desc':company_desc,
            'skills_required':",".join(skills_required),
            'gender':gender,
            'military_service':military_service,
            'education':",".join(education),
            'experience':experience,
            'age_range':age_range
        }
        
        
            