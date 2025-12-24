import pymysql
import json
import uuid

# 数据库连接配置
DB_CONFIG = {
    'host': '43.138.171.198',
    'port': 3306,
    'user': 'root',
    'password': 'rtkcXFAAdeRD7hhs',
    'charset': 'utf8mb4'
}

def generate_uuid():
    return str(uuid.uuid4())

def init_database():
    # 连接MySQL服务器（不指定数据库）
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS dong_legal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE dong_legal")

        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                phone_number VARCHAR(20) UNIQUE,
                role VARCHAR(10) DEFAULT 'USER',
                enterprise_name VARCHAR(100),
                approval_status VARCHAR(10) DEFAULT 'PENDING',
                is_certified BOOLEAN DEFAULT FALSE,
                avatar_url TEXT
            )
        """)

        # 创建文档模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_templates (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                content LONGTEXT,
                file_url TEXT
            )
        """)

        # 创建风险场景表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_scenarios (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                risk_level VARCHAR(10),
                content TEXT,
                questions TEXT
            )
        """)

        # 创建证据清单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_lists (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                items TEXT
            )
        """)

        # 创建民法典表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS civil_code_articles (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                content TEXT NOT NULL
            )
        """)

        # 创建物业公司表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enterprises (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            )
        """)

        # 创建系统配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_configs (
                id VARCHAR(36) PRIMARY KEY,
                enable_phone_login BOOLEAN DEFAULT TRUE,
                welcome_message TEXT,
                ai_knowledge_base TEXT,
                enterprise_logo TEXT,
                splash_image TEXT
            )
        """)

        # 创建自定义海报表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_posters (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                image_base64 LONGTEXT
            )
        """)

        # 创建联系二维码表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_qr_codes (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                image_base64 LONGTEXT
            )
        """)

        connection.commit()
        print("数据库表结构创建成功")

        # 插入默认数据
        insert_default_data(cursor, connection)

    except Exception as e:
        print(f"数据库初始化失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def insert_default_data(cursor, connection):
    try:
        # 清空现有数据（可选）
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE users")
        cursor.execute("TRUNCATE TABLE document_templates")
        cursor.execute("TRUNCATE TABLE risk_scenarios")
        cursor.execute("TRUNCATE TABLE evidence_lists")
        cursor.execute("TRUNCATE TABLE civil_code_articles")
        cursor.execute("TRUNCATE TABLE enterprises")
        cursor.execute("TRUNCATE TABLE system_configs")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 插入默认用户
        default_users = [
            ('1', 'admin', 'admin', '13800000000', 'ADMIN', '东元物业', 'APPROVED', True, None),
            ('2', 'user1', '123', '13900000000', 'USER', '东元示范物业', 'APPROVED', True, None),
            ('3', 'zmh123', '123456', '13700000000', 'USER', '东元示范物业', 'APPROVED', True, None)
        ]

        cursor.executemany("""
            INSERT INTO users (id, username, password, phone_number, role, enterprise_name, approval_status, is_certified, avatar_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, default_users)

        # 插入文档模板
        default_docs = [
            ('1', '前期物业服务合同', '前介承接', '含承接查验及交房环节的关键风险防控条款', '【前期物业服务合同】\n第一条 委托方(建设单位)：[单位名称]\n第二条 受托方(物业服务人)：[公司名称]\n...\n[此处为东元法务部审核的标准化条款]...', None),
            ('2', '催缴物业费律师函', '纠纷告知', '由东元律师团审核，具备司法证据效力的正式告知函', '【律师函：限期缴纳告知】\n致[业主姓名/房号]：\n根据《民法典》第九百四十四条规定，业主应当按照约定向物业服务人支付物业费...\n如逾期未缴纳，我司将依法提起诉讼...', None)
        ]

        cursor.executemany("""
            INSERT INTO document_templates (id, title, category, description, content, file_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, default_docs)

        # 插入风险场景
        default_risks = [
            ('s1', '保安外包合规性自查', 'Medium', None, json.dumps([
                '保安服务合同是否明确约定了造成第三方损失的赔偿责任主体？',
                '是否已留存外包保安人员的无犯罪记录证明复印件？',
                '是否约定了保安人员的年龄上限及健康状况要求？',
                '是否有对外包公司定期的履约评价记录？'
            ])),
            ('s2', '电梯维保合同风险筛查', 'High', None, json.dumps([
                '维保合同是否包含年度年检费用的承担方？',
                '是否明确了困人故障的到达现场时限？',
                '是否有关于配件更换价格的预先约定清单？'
            ])),
            ('s3', '节前小区安全隐患排查', 'Low', None, json.dumps([
                '消防泵房/消火栓是否处于正常工作状态并有巡检记录？',
                '公共区域及应急逃生通道是否已清理杂物且无电动车停放？',
                '化粪池、雨污水管道是否已进行节前清掏或排查？',
                '节日期间值班表是否已公示并确认关键岗位人员在岗？'
            ]))
        ]

        cursor.executemany("""
            INSERT INTO risk_scenarios (id, title, risk_level, content, questions)
            VALUES (%s, %s, %s, %s, %s)
        """, default_risks)

        # 插入证据清单
        default_evidence = [
            ('e1', '物业费追缴（个人）', json.dumps([
                "房产所有权证明/购房合同复印件",
                "《物业服务合同》（需含收费标准条款）",
                "欠费明细清单（加盖财务公章）",
                "律师函/催费通知单的送达凭证（如挂号信回执）",
                "公示记录照片（如小区公告栏催费公示）"
            ])),
            ('e2', '违章装修/改变外立面', json.dumps([
                "《装修管理协议》签署原件",
                "现场违章施工照片（多角度且包含时间水印）",
                "《整改通知书》及拒绝签收记录",
                "原始建筑设计图纸（对比违规部分）",
                "劝阻过程的录音录像资料"
            ])),
            ('e3', '高空抛物侵权', json.dumps([
                "公共区域监控视频拷贝",
                "现场血迹/损坏物品封存照片",
                "派出所报警回执/询问笔录",
                "物业已尽安全保障义务证明（如警示标识照片、巡检记录）",
                "证人证言及其联系方式"
            ]))
        ]

        cursor.executemany("""
            INSERT INTO evidence_lists (id, title, items)
            VALUES (%s, %s, %s)
        """, default_evidence)

        # 插入民法典条文
        default_laws = [
            ('271', '第二百七十一条', '业主对建筑物内的住宅、经营性用房等专有部分享有所有权，对专有部分以外的共有部分享有共有和共同管理的权利。'),
            ('277', '第二百七十七条', '业主可以设立业主大会，选举业主委员会。地方人民政府有关部门、居民委员会应当对设立业主大会和选举业主委员会给予指导和协助。'),
            ('284', '第二百八十四条', '业主可以自行管理建筑物及其附属设施，也可以委托物业服务企业或者其他管理人管理。对建设单位聘请的物业服务企业或者其他管理人，业主有权依法更换。'),
            ('937', '第九百三十七条', '物业服务合同是物业服务人在物业服务区域内，为业主提供建筑物及其附属设施的维修养护、环境卫生和相关秩序的管理维护等物业服务，业主支付物业费的合同。'),
            ('944', '第九百四十四条', '业主应当按照约定向物业服务人支付物业费。物业服务人已经按照约定和有关规定提供服务的，业主不得以未接受或者无需接受相关物业服务为由拒绝支付物业费。')
        ]

        cursor.executemany("""
            INSERT INTO civil_code_articles (id, title, content)
            VALUES (%s, %s, %s)
        """, default_laws)

        # 插入物业公司
        default_enterprises = [
            ('ent1', '东元示范物业'),
            ('ent2', '万科物业'),
            ('ent3', '碧桂园服务'),
            ('ent4', '龙湖智慧服务')
        ]

        cursor.executemany("""
            INSERT INTO enterprises (id, name)
            VALUES (%s, %s)
        """, default_enterprises)

        # 插入系统配置
        default_welcome = '您好！我是东元物业法务助手。我可以为您提供《民法典》咨询、文书草拟及风险建议。（回答仅供参考）'
        default_ai_kb = '东元法务助手：遵循《民法典》。专注于物业费收缴、违章装修、公共部位纠纷。回复专业、严谨。'

        cursor.execute("""
            INSERT INTO system_configs (id, enable_phone_login, welcome_message, ai_knowledge_base)
            VALUES (%s, %s, %s, %s)
        """, (generate_uuid(), True, default_welcome, default_ai_kb))

        connection.commit()
        print("默认数据插入成功")

    except Exception as e:
        print(f"插入默认数据失败: {e}")
        connection.rollback()

if __name__ == "__main__":
    init_database()
    print("数据库初始化完成！")