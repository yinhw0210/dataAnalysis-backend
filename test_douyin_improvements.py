#!/usr/bin/env python3
"""
抖音解析改进测试脚本
Test script for Douyin parsing improvements
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app.douyin.index import Douyin
from src.utils import get_analyze_logger

logger = get_analyze_logger()


async def test_single_video(url: str, description: str = ""):
    """测试单个视频解析"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"URL: {url}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        
        # 创建抖音解析实例
        douyin = Douyin(url, "png")
        
        # 异步初始化
        await douyin.initialize()
        
        # 获取结果
        result = douyin.to_dict()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 分析结果
        if result and result.get("code") == 200:
            video_data = result.get("data", {}).get("video_data")
            if video_data and len(str(video_data)) > 100:  # 简单检查是否有实际数据
                print(f"✅ 成功: 获取到视频数据")
                print(f"⏱️  耗时: {duration:.2f}秒")
                print(f"📊 数据大小: {len(str(video_data))} 字符")
                return True
            else:
                print(f"❌ 失败: 返回数据为空或无效")
                print(f"📄 响应: {result}")
                return False
        else:
            print(f"❌ 失败: API调用失败")
            print(f"📄 响应: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        logger.error(f"测试异常: {str(e)}", exc_info=True)
        return False


async def test_multiple_videos():
    """测试多个视频解析"""
    test_urls = [
        {
            "url": "https://v.douyin.com/ieFsaUmj/",
            "description": "测试视频1"
        },
        {
            "url": "https://v.douyin.com/ieFp2KLH/", 
            "description": "测试视频2"
        },
        {
            "url": "https://v.douyin.com/ieFpqn4B/",
            "description": "测试视频3"
        }
    ]
    
    success_count = 0
    total_count = len(test_urls)
    
    print(f"\n🚀 开始批量测试 ({total_count} 个视频)")
    
    for i, test_case in enumerate(test_urls, 1):
        print(f"\n📹 测试进度: {i}/{total_count}")
        
        success = await test_single_video(
            test_case["url"], 
            test_case["description"]
        )
        
        if success:
            success_count += 1
            
        # 添加延迟避免请求过于频繁
        if i < total_count:
            print(f"⏳ 等待 5 秒后继续下一个测试...")
            await asyncio.sleep(5)
    
    # 输出测试总结
    success_rate = (success_count / total_count) * 100
    print(f"\n{'='*60}")
    print(f"📊 测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_count}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {total_count - success_count}")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"🎉 测试结果: 优秀 (成功率 ≥ 80%)")
    elif success_rate >= 60:
        print(f"✅ 测试结果: 良好 (成功率 ≥ 60%)")
    elif success_rate >= 40:
        print(f"⚠️  测试结果: 一般 (成功率 ≥ 40%)")
    else:
        print(f"❌ 测试结果: 需要改进 (成功率 < 40%)")
    
    return success_rate


async def test_anti_detection_features():
    """测试反检测功能"""
    print(f"\n🛡️  测试反检测功能")
    print(f"{'='*60}")

    try:
        from src.crawlers.douyin.anti_detection import AntiDetectionManager, CookieManager

        # 测试浏览器指纹生成
        fingerprint = AntiDetectionManager.get_random_fingerprint()
        print(f"✅ 浏览器指纹生成: {fingerprint['user_agent'][:50]}...")

        # 测试请求头生成
        base_headers = {"User-Agent": "test"}
        enhanced_headers = AntiDetectionManager.generate_realistic_headers(base_headers)
        print(f"✅ 请求头增强: 添加了 {len(enhanced_headers)} 个头部字段")

        # 测试参数生成
        base_params = {"aweme_id": "test"}
        realistic_params = AntiDetectionManager.generate_realistic_params(base_params)
        print(f"✅ 参数优化: 生成了 {len(realistic_params)} 个参数")

        # 测试Cookie验证
        test_cookie = "sessionid=test; sid_tt=test; uid_tt=test; " + "x" * 200
        is_valid = CookieManager.validate_cookie_freshness(test_cookie)
        print(f"✅ Cookie验证: {'通过' if is_valid else '失败'}")

        print(f"🛡️  反检测功能测试完成")
        return True

    except Exception as e:
        print(f"❌ 反检测功能测试失败: {str(e)}")
        return False


async def test_bypass_detection():
    """测试检测绕过功能"""
    print(f"\n🚀 测试检测绕过功能")
    print(f"{'='*60}")

    try:
        from src.crawlers.douyin.bypass_detection import DouyinBypassManager

        test_aweme_id = "7533613909853424955"
        test_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": "test_cookie"
        }

        # 测试Web端绕过
        print("🔄 测试Web端检测绕过...")
        web_result = await DouyinBypassManager.bypass_web_detection(test_aweme_id, test_headers)
        print(f"Web端绕过结果: {'成功' if web_result else '失败'}")

        # 测试移动端绕过
        print("🔄 测试移动端检测绕过...")
        mobile_result = await DouyinBypassManager.bypass_mobile_detection(test_aweme_id)
        print(f"移动端绕过结果: {'成功' if mobile_result else '失败'}")

        # 测试紧急备用方案
        print("🔄 测试紧急备用方案...")
        fallback_result = await DouyinBypassManager.emergency_fallback(test_aweme_id)
        print(f"紧急备用方案: {'成功' if fallback_result else '失败'}")

        print(f"🚀 检测绕过功能测试完成")
        return True

    except Exception as e:
        print(f"❌ 检测绕过功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print(f"🔧 抖音解析改进测试 (多策略版本)")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 测试反检测功能
    await test_anti_detection_features()

    # 测试检测绕过功能
    await test_bypass_detection()

    # 测试单个视频
    print(f"\n📹 单个视频测试")
    await test_single_video(
        "https://v.douyin.com/ieFsaUmj/",
        "单个视频解析测试 (多策略)"
    )

    # 测试多个视频
    success_rate = await test_multiple_videos()

    # 输出最终结果
    print(f"\n🏁 测试完成")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if success_rate >= 60:
        print(f"🎉 改进效果: 显著提升")
        print(f"💡 建议: 继续监控和优化")
    elif success_rate >= 20:
        print(f"⚠️  改进效果: 部分成功")
        print(f"💡 建议: 至少紧急备用方案可以工作")
    else:
        print(f"❌ 改进效果: 需要进一步优化")
        print(f"💡 建议: 检查Cookie有效性和网络环境")

    print(f"\n📋 详细日志请查看: logs/analyze_{datetime.now().strftime('%Y-%m-%d')}.log")
    print(f"\n🔧 新增功能:")
    print(f"  - 多策略解析 (5种不同策略)")
    print(f"  - 检测绕过机制")
    print(f"  - 紧急备用方案")
    print(f"  - 移动端API模拟")
    print(f"  - HTML数据提取")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
