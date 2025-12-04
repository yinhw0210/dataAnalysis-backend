#!/usr/bin/env python3
"""
抖音解析快速测试脚本
Quick test script for Douyin parsing
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app.douyin.index import Douyin
from src.utils import get_analyze_logger

logger = get_analyze_logger()


async def quick_test():
    """快速测试抖音解析"""
    print(f"🚀 抖音解析快速测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    test_url = "https://v.douyin.com/ieFsaUmj/"
    
    try:
        print(f"📹 测试URL: {test_url}")
        
        # 创建抖音解析实例
        douyin = Douyin(test_url, "png")
        
        print(f"🔄 开始解析...")
        
        # 异步初始化
        await douyin.initialize()
        
        # 获取结果
        result = douyin.to_dict()
        
        print(f"✅ 解析完成")
        print(f"📊 结果状态: {result.get('code', 'unknown')}")
        
        if result.get('code') == 200:
            video_data = result.get('data', {}).get('video_data')
            if video_data:
                print(f"🎉 成功获取视频数据")
                print(f"📝 视频描述: {video_data.get('desc', 'N/A')[:50]}...")
                print(f"👤 作者: {video_data.get('author', {}).get('nickname', 'N/A')}")
                print(f"❤️  点赞数: {video_data.get('statistics', {}).get('digg_count', 'N/A')}")
                return True
            else:
                print(f"❌ 未获取到视频数据")
                return False
        else:
            print(f"❌ 解析失败，状态码: {result.get('code')}")
            print(f"📄 错误信息: {result.get('message', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"💥 测试异常: {str(e)}")
        logger.error(f"快速测试异常: {str(e)}", exc_info=True)
        return False


async def test_bypass_only():
    """仅测试绕过检测功能"""
    print(f"\n🛡️  测试绕过检测功能")
    print(f"{'='*60}")
    
    try:
        from src.crawlers.douyin.bypass_detection import DouyinBypassManager
        
        test_aweme_id = "7533613909853424955"
        
        # 测试紧急备用方案
        print(f"🆘 测试紧急备用方案...")
        fallback_result = await DouyinBypassManager.emergency_fallback(test_aweme_id)
        
        if fallback_result:
            print(f"✅ 紧急备用方案成功")
            print(f"📊 返回数据: {len(str(fallback_result))} 字符")
            
            # 检查数据结构
            if isinstance(fallback_result, dict) and 'aweme_list' in fallback_result:
                aweme_list = fallback_result['aweme_list']
                if aweme_list and len(aweme_list) > 0:
                    aweme = aweme_list[0]
                    print(f"📝 视频ID: {aweme.get('aweme_id', 'N/A')}")
                    print(f"📝 描述: {aweme.get('desc', 'N/A')}")
                    print(f"👤 作者: {aweme.get('author', {}).get('nickname', 'N/A')}")
                    return True
        
        print(f"❌ 紧急备用方案失败")
        return False
        
    except Exception as e:
        print(f"💥 绕过测试异常: {str(e)}")
        return False


async def main():
    """主函数"""
    print(f"🔧 抖音解析多策略解决方案测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: 完整解析流程
    success1 = await quick_test()
    
    # 测试2: 仅绕过检测
    success2 = await test_bypass_only()
    
    # 总结
    print(f"\n🏁 测试总结")
    print(f"{'='*60}")
    print(f"完整解析测试: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"绕过检测测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1:
        print(f"🎉 多策略解决方案工作正常！")
        print(f"💡 建议: 继续使用当前配置")
    elif success2:
        print(f"⚠️  至少紧急备用方案可以工作")
        print(f"💡 建议: 检查Cookie和网络配置")
    else:
        print(f"❌ 所有测试都失败了")
        print(f"💡 建议: 检查代码配置和网络连接")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 详细日志: logs/analyze_{datetime.now().strftime('%Y-%m-%d')}.log")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
